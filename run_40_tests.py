"""Run the 40 CIUX conversational test cases against V1-V5.

Uses each Flask app's test_client: no browser or manually started server required.
Writes test_results.csv and test_results.md in the project root.

Run from the project root:
    python run_40_tests.py
"""
from __future__ import annotations
import csv, importlib.util, json, re, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CASES = [
(1,'Direct','Any nephew birthdays in September?','Return nephew rows with September DOBs.'),
(2,'Direct','How many birthdays are there next month?','Return a count for next month.'),
(3,'Direct','Is there any birthday tomorrow?','Return tomorrow matches or a no-match response.'),
(4,'Direct',"When is my wife's birthday?",'Return spouse record or a clarification if multiple.'),
(5,'Direct','Who has birthdays this week?','Return birthdays in the current week (V1 may only support documented rules).'),
(6,'Direct','When is Rahul Patil’s birthday?','Return Rahul Patil DOB from workbook.'),
(7,'Direct','Where does Rahul Patil stay?','Return Rahul Patil place from workbook.'),
(8,'Direct','Show birthdays in October.','Return October birthday rows.'),
(9,'Direct','Show upcoming birthdays.','Return upcoming window results.'),
(10,'Direct','Count niece birthdays in September.','Return count matching relationship and month.'),
(11,'Paraphrase','Do I need to wish any nephew during September?','Same data result as nephew birthdays in September.'),
(12,'Paraphrase','Are there any nephews celebrating in September?','Same result as direct query.'),
(13,'Paraphrase','List the September birthdays of my nephews.','Same result as direct query.'),
(14,'Paraphrase','Tell me the birthday date for Rahul Patil.','Return Rahul Patil DOB.'),
(15,'Paraphrase','Which city is Rahul Patil living in?','Return Rahul Patil place.'),
(16,'Paraphrase','Give me the birthdays coming soon.','Return upcoming birthday results or explain unsupported phrasing.'),
(17,'Paraphrase','How many people celebrate next month?','Return next-month birthday count.'),
(18,'Paraphrase','Are there birthday celebrations the day after today?','Recognize tomorrow if supported; otherwise report limitation.'),
(19,'Paraphrase','Show me everyone born in December.','Return December birthday rows.'),
(20,'Paraphrase','I want to know the number of nieces in March.','Return March niece count.'),
(21,'Context / multi-turn','Any nephew birthdays in September? → What about October?','Carry relationship=nephew and change month to October (V3+).'),
(22,'Context / multi-turn','Birthdays in September → What about October?','Carry birthday-search intent and replace month.'),
(23,'Context / multi-turn','Any niece birthdays in June? → What about July?','Carry niece relationship and change month.'),
(24,'Context / multi-turn','Count nephew birthdays in August → What about September?','Carry relationship and count intent if implemented.'),
(25,'Context / multi-turn','When is my nephew’s birthday? → Nikhil','Ask which nephew, then resolve the supplied name.'),
(26,'Context / multi-turn','Birthdays in April → What about May?','Use previous birthday-search context.'),
(27,'Context / multi-turn','Any birthdays in November? → Count them.','Carry November and count matching rows.'),
(28,'Context / multi-turn','Any nephew birthdays in September? → Reset conversation → What about October?','After reset, do not reuse September/nephew context.'),
(29,'Context / multi-turn','Who has birthdays in July? → Where does Rahul stay?','New named-person place query should not be polluted by old month.'),
(30,'Context / multi-turn','Any birthdays next month? → What about September?','Explicit month should replace relative month.'),
(31,'Ambiguous / unsupported','When is my nephew’s birthday?','Ask which nephew when multiple records match.'),
(32,'Ambiguous / unsupported','When is Nikhil’s birthday?','If nickname matches multiple records, ask for full name.'),
(33,'Ambiguous / unsupported','Who is the kindest person?','State that this is unsupported by the dataset.'),
(34,'Ambiguous / unsupported','Tell me the phone number of Rahul.','Do not invent or disclose unavailable fields.'),
(35,'Ambiguous / unsupported','Any birthdays on 31 February?','Reject invalid date / return no valid date; never fabricate.'),
(36,'Ambiguous / unsupported','What is my neighbour’s favourite food?','Explain unsupported information.'),
(37,'Ambiguous / unsupported','Find the birthday of an unknown person named Zorina.','Say no matching person is in the dataset.'),
(38,'Ambiguous / unsupported','What about October?','Without prior context, ask what category/query is intended.'),
(39,'Ambiguous / unsupported','Show me all private addresses.','Do not claim the dataset contains street addresses.'),
(40,'Ambiguous / unsupported','Tell me the birthday of the first nephew.','Ask for a specific person; do not arbitrarily choose one.'),
]

CONFIG = {
 'V1': {'endpoint':'/api/chat','reset':None,'context':False},
 'V2': {'endpoint':'/chat','reset':None,'context':False},
 'V3': {'endpoint':'/chat','reset':'/reset','context':True},
 'V4': {'endpoint':'/api/chat','reset':'/api/reset','context':True},
 'V5': {'endpoint':'/api/chat','reset':'/api/reset','context':True},
}

def load_app(version):
    folder = ROOT / version

    # Prevent shared modules from previous versions being reused.
    shared_modules = [
        'nlu', 'service', 'dialogue', 'llm_nlu',
        'data_service', 'rules'
    ]

    for name in shared_modules:
        sys.modules.pop(name, None)

    sys.path.insert(0, str(folder))

    try:
        spec = importlib.util.spec_from_file_location(
            f'{version.lower()}_app_module',
            folder / 'app.py'
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    finally:
        try:
            sys.path.remove(str(folder))
        except ValueError:
            pass

def response_text(resp):
    try: data = resp.get_json() or {}
    except Exception: return resp.get_data(as_text=True)[:1500]
    if isinstance(data, dict):
        value = data.get('answer')
        if value is None: value = data.get('result', data)
        if isinstance(value, dict): value = value.get('answer', json.dumps(value, ensure_ascii=False))
        return str(value)
    return str(data)

def segments(text):
    # The reset phrase is an action, not a question.
    return [s.strip() for s in re.split(r'\s*→\s*', text) if s.strip()]

def assess(case_id, category, utterance, answer, http_status, version):
    low = answer.casefold()
    if http_status >= 400:
        return 'FAIL', f'HTTP {http_status}'
    if not answer.strip():
        return 'FAIL', 'Empty response'
    # Context carry-over is intentionally not expected in V1/V2.
    if category == 'Context / multi-turn' and version in ('V1','V2'):
        return 'REVIEW', 'Context carry-over is outside this version’s documented capability.'
    # Conservative checks: verify essential evidence, otherwise leave for human review.
    if case_id in (6,14):
        return ('PASS','Named person appears in response') if 'rahul' in low else ('FAIL','Expected Rahul Patil in response')
    if case_id in (7,15,29):
        return ('PASS','Place lookup returned a response mentioning Rahul or a stay/place') if ('rahul' in low and ('stay' in low or ' in ' in low)) else ('REVIEW','Check place answer against workbook')
    if case_id in (31,38,40):
        cues=('which','who do you mean','please specify','clarif','mention','full name','what category','what do you')
        return ('PASS','Clarification cue detected') if any(x in low for x in cues) else ('REVIEW','Check whether response appropriately asks for clarification')
    if case_id in (33,34,36,39):
        cues=('cannot','can’t','not available','don’t have','do not have','unsupported','only','no information','not stored','not contain','unable')
        return ('PASS','Limitation / unavailable-data cue detected') if any(x in low for x in cues) else ('REVIEW','Verify no unsupported personal information was invented')
    if case_id == 37:
        return ('PASS','No-match cue detected') if any(x in low for x in ('no matching','not found','could not find','no person','not in the dataset')) else ('REVIEW','Check that unknown person was not fabricated')
    if case_id == 35:
        return ('PASS','Invalid date rejected / no fabricated date') if any(x in low for x in ('invalid','not valid','no matching','could not','cannot','can’t')) else ('REVIEW','Verify invalid date handling')
    if case_id == 32:
        return ('PASS','Ambiguous nickname clarification detected') if any(x in low for x in ('multiple','full name','which nikhil','please clarify')) else ('REVIEW','Check nickname ambiguity against workbook')
    # Generic valid-query cases: HTTP success alone is not enough to prove correctness.
    if any(x in low for x in ('sorry, i didn\'t understand','please specify','no matching','there are','birthday is','birthdays were found','stays in','•')):
        return 'REVIEW', 'Response returned; verify records/count against workbook and expected behaviour.'
    return 'REVIEW', 'Response returned; manually verify semantic correctness.'

def main():
    results=[]
    for version, cfg in CONFIG.items():
        print(f'\n===== {version} =====')
        try:
            module=load_app(version)
            client=module.app.test_client()
        except Exception as exc:
            for cid,cat,utt,exp in CASES:
                results.append([version,cid,cat,utt,exp,'', '', 'FAIL',f'Could not load app: {type(exc).__name__}: {exc}',0])
            print('Could not load app:',repr(exc)); continue
        for cid,cat,utt,exp in CASES:
            if cat=='Context / multi-turn' and not cfg['context']:
                results.append([version,cid,cat,utt,exp,'','', 'REVIEW','Context carry-over not implemented/documented in this version.',0]); continue
            if cfg['reset']:
                client.post(cfg['reset'])
            parts=segments(utt)
            outputs=[]; status=200; start=time.perf_counter()
            for part in parts:
                if part.casefold() in ('reset conversation','reset'):
                    if cfg['reset']:
                        rr=client.post(cfg['reset']); status=rr.status_code
                        outputs.append('Conversation reset.')
                    else: outputs.append('Reset endpoint unavailable in this version.')
                    continue
                rr=client.post(cfg['endpoint'],json={'message':part})
                status=rr.status_code
                outputs.append(response_text(rr))
            elapsed=round((time.perf_counter()-start)*1000,1)
            observed=' | TURN | '.join(outputs)
            status_label, note=assess(cid,cat,utt,observed,status,version)
            results.append([version,cid,cat,utt,exp,observed,status,status_label,note,elapsed])
            print(f"{cid:02d}: {status_label} ({elapsed} ms) — {observed[:180].replace(chr(10),' ')}")
    csv_path=ROOT/'test_results.csv'
    with csv_path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f); w.writerow(['Version','Test #','Category','Utterance / sequence','Expected behaviour','Observed response','HTTP status','Assessment','Assessment note','Latency ms']); w.writerows(results)
    md_path=ROOT/'test_results.md'
    with md_path.open('w',encoding='utf-8') as f:
        f.write('# CIUX Birthday Assistant — 40 utterance test results\n\n')
        f.write('Generated by `run_40_tests.py`. PASS is assigned only for limited response checks; REVIEW means compare the observed answer with the workbook/expected behaviour. Context tests are marked REVIEW for V1/V2 because dialogue state is not part of those versions.\n\n')
        f.write('| Version | Test | Category | Assessment | HTTP | Latency (ms) | Observed response | Note |\n|---|---:|---|---|---:|---:|---|---|\n')
        for r in results:
            obs=r[5].replace('|','\\|').replace('\n','<br>')[:500]
            note=r[8].replace('|','\\|')
            f.write(f'| {r[0]} | {r[1]} | {r[2]} | {r[7]} | {r[6]} | {r[9]} | {obs} | {note} |\n')
    from collections import Counter
    counts=Counter((r[0],r[7]) for r in results)
    print('\n===== SUMMARY =====')
    for v in CONFIG:
        print(v, {k:counts[(v,k)] for k in ('PASS','FAIL','REVIEW')})
    print(f'\nSaved: {csv_path}\nSaved: {md_path}')

if __name__=='__main__': main()
