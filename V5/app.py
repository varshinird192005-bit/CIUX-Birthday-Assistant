import os
from flask import Flask,render_template,request,jsonify,session
from service import load_people,execute
from nlu import parse
from dialogue import enrich_with_context,update_state
app=Flask(__name__); app.secret_key=os.getenv('FLASK_SECRET','local-development-secret-change-me'); PEOPLE=load_people()
from llm_nlu import parse_with_llm
def normalize(parsed):
    e=parsed.setdefault('entities',{})
    if e.get('person_name'):
        matches=PEOPLE[PEOPLE.Name.str.casefold()==str(e['person_name']).casefold()]
        if len(matches)==1: e['person_id']=str(matches.iloc[0].Person_ID)
        else: e.pop('person_id',None)
    if e.get('relationship'):
        valid={str(x).casefold():str(x) for x in PEOPLE.Relationship.unique()}
        e['relationship']=valid.get(str(e['relationship']).casefold(),e['relationship'])
    if e.get('month') and not (isinstance(e['month'],int) and 1<=e['month']<=12):
        import calendar
        names={m.lower():i for i,m in enumerate(calendar.month_name) if m}
        e['month']=names.get(str(e['month']).lower())
        if e['month'] is None: e.pop('month',None)
    return parsed

@app.get('/')
def index(): return render_template('index.html',record_count=len(PEOPLE))
@app.post('/api/chat')
def chat():
    msg=(request.get_json(silent=True) or {}).get('message',''); state=session.get('dialogue_state',{}); trace=[]
    parsed=None
    if os.getenv('OPENAI_API_KEY'):
        try: parsed=normalize(parse_with_llm(msg)); trace.append('LLM used for NLU only; structured data remains authoritative.')
        except Exception as exc: trace.append(f'LLM unavailable/invalid; rule fallback used ({type(exc).__name__}).')
    if parsed is None: parsed=parse(msg,PEOPLE); trace.append('Rule-based NLU used.')
    parsed=enrich_with_context(parsed,state)
    e=parsed.get('entities',{})
    if e.get('ambiguous_nickname'):
        answer='I found multiple people with that nickname: '+', '.join(e['ambiguous_nickname'])+'. Please use a full name.'
    elif e.get('relationship') and not e.get('person_id') and 'when is my' in msg.lower():
        matches=PEOPLE[PEOPLE.Relationship.str.casefold()==str(e['relationship']).casefold()]
        if len(matches)>1: answer=f"I found {len(matches)} people recorded as {e['relationship']}: "+', '.join(matches.Name.head(8))+'. Which one do you mean?'
        else: answer=execute(parsed,PEOPLE)
    else: answer=execute(parsed,PEOPLE)
    session['dialogue_state']=update_state(parsed,state)
    trace.extend([f"Intent: {parsed['intent']}",f"Entities/context: {e}","Query service reads data/people.xlsx."])
    return jsonify(answer=answer,trace=trace,state=session['dialogue_state'])
@app.post('/api/reset')
def reset(): session.pop('dialogue_state',None); return jsonify(ok=True,message='Conversation context cleared.')
@app.get('/api/health')
def health(): return jsonify(status='ok',records=len(PEOPLE),version='V5')
if __name__=='__main__': app.run(host='127.0.0.1',port=5000,debug=True)
