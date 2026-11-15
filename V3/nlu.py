import calendar, re
MONTHS={m.lower():i for i,m in enumerate(calendar.month_name) if m}
RELATIONS=['sister-in-law','brother-in-law','nephew','niece','wife','father','mother','brother','sister','uncle','aunt','cousin','friend','colleague','student','neighbour']
def parse(message, people):
    text=(message or '').lower().strip(); out={'intent':'unknown','entities':{}}; e=out['entities']
    if not text: return out
    if any(x in text for x in ['how many','count','number of']): out['intent']='count_birthdays'
    elif any(x in text for x in ['where','stay','live','place']): out['intent']='person_place'
    elif any(x in text for x in ['upcoming','coming birthdays','next 30 days']): out['intent']='upcoming_birthdays'
    else: out['intent']='birthday_search'
    if 'tomorrow' in text: e['relative_date']='tomorrow'
    elif 'upcoming' in text: e['relative_date']='upcoming'
    if 'next month' in text: e['relative_month']='next'
    for m,n in MONTHS.items():
        if re.search(r'\b'+m+r'\b',text): e['month']=n; break
    for rel in sorted(RELATIONS,key=len,reverse=True):
        if re.search(r'\b'+re.escape(rel)+r's?\b',text): e['relationship']=rel.title().replace('In-law','-in-law'); break
    # Full names are resolved before nicknames; ambiguous nicknames are not guessed.
    for _,row in people.iterrows():
        name=str(row['Name']).strip()
        if name and re.search(r'\b'+re.escape(name.lower())+r'\b',text):
            e['person_id']=str(row['Person_ID']); e['person_name']=name; break
    if 'person_id' not in e:
        matches=[]
        for _,row in people.iterrows():
            nick=str(row.get('Nickname','')).strip()
            if len(nick)>=3 and re.search(r'\b'+re.escape(nick.lower())+r'\b',text): matches.append(row)
        if len(matches)==1: e['person_id']=str(matches[0]['Person_ID']); e['person_name']=str(matches[0]['Name'])
        elif len(matches)>1: e['ambiguous_nickname']=sorted({str(x['Name']) for x in matches})
    return out
