from datetime import date, timedelta
import calendar
import pandas as pd

def load_people(path=None):
    from pathlib import Path
    p = Path(path) if path else Path(__file__).resolve().parent / "data" / "people.xlsx"
    df = pd.read_excel(p, sheet_name="People")
    required = {"Person_ID","Name","Nickname","DOB","Place_of_Stay","Relationship","Relationship_Group","Relationship_Detail"}
    missing = required - set(df.columns)
    if missing: raise ValueError(f"Dataset missing columns: {sorted(missing)}")
    df = df.copy(); df["DOB"] = pd.to_datetime(df["DOB"], errors="coerce")
    if df["DOB"].isna().any(): raise ValueError("Dataset contains invalid DOB values")
    for c in required - {"Person_ID","DOB"}: df[c] = df[c].fillna("").astype(str).str.strip()
    if df["Person_ID"].duplicated().any(): raise ValueError("Person_ID values must be unique")
    return df

def next_birthday(dob, today):
    try: d = date(today.year, dob.month, dob.day)
    except ValueError: d = date(today.year, 2, 28)
    if d < today:
        try: d = date(today.year + 1, dob.month, dob.day)
        except ValueError: d = date(today.year + 1, 2, 28)
    return d

def format_rows(rows, today=None, include_year=False):
    today = today or date.today()
    if rows.empty: return "No matching birthdays were found."
    result=[]
    for _, r in rows.iterrows():
        d=r.DOB.date(); nb=next_birthday(d,today); suffix=f" {d.year}" if include_year else ""
        result.append(f"• {r['Name']} — {d.strftime('%d %B')}{suffix} ({r['Relationship']})")
    return "\n".join(result)

def execute(parsed, df, today=None):
    today=today or date.today(); e=parsed.get("entities",{}); intent=parsed.get("intent","unknown"); work=df.copy()
    if e.get("person_id"):
        hit=df[df.Person_ID.astype(str)==str(e['person_id'])]
        if len(hit)==1:
            r=hit.iloc[0]
            if intent=="person_place": return f"{r['Name']} stays in {r['Place_of_Stay']}."
            return f"{r['Name']}'s birthday is {r.DOB.strftime('%d %B %Y')}."
    if e.get("person_name") and not e.get("person_id"):
        candidates=df[df.Name.str.casefold()==str(e['person_name']).casefold()]
        if len(candidates)==1:
            r=candidates.iloc[0]
            return f"{r['Name']}'s birthday is {r.DOB.strftime('%d %B %Y')}."
    rel=e.get("relationship")
    if rel: work=work[work.Relationship.str.casefold()==str(rel).casefold()]
    month=e.get("month")
    if e.get("relative_month")=="next": month=(today.month%12)+1
    if e.get("relative_date")=="tomorrow":
        t=today+timedelta(days=1); work=work[(work.DOB.dt.month==t.month)&(work.DOB.dt.day==t.day)]
    elif month: work=work[work.DOB.dt.month==int(month)]
    elif intent=="upcoming_birthdays" or e.get("relative_date")=="upcoming":
        rows=[]
        for idx,r in work.iterrows():
            nb=next_birthday(r.DOB.date(),today); delta=(nb-today).days
            if 0<=delta<=30: rows.append((nb,idx))
        work=work.loc[[idx for _,idx in sorted(rows)]]
    elif intent=="birthday_search" and not rel and not e.get("relative_date"):
        return "Please specify a person, relationship, month or date range. Type 'help' for examples."
    if intent=="count_birthdays": return f"There are {len(work)} matching birthdays."
    if intent=="person_place":
        if rel and work.empty: return "No matching people were found."
        return "Please mention a person's name to look up their place of stay."
    if month: work=work.assign(_day=work.DOB.dt.day).sort_values(["_day","Name"]).drop(columns=["_day"])
    else: work=work.assign(_next=work.DOB.apply(lambda x: next_birthday(x.date(),today))).sort_values(["_next","Name"]).drop(columns=["_next"])
    return format_rows(work,today)
