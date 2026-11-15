from __future__ import annotations

from datetime import date, timedelta
import calendar
import re
import pandas as pd

MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}

RELATIONSHIP_ALIASES = {
    "wife": "Wife", "spouse": "Wife",
    "father": "Father", "dad": "Father", "appa": "Father",
    "mother": "Mother", "mom": "Mother", "amma": "Mother",
    "brother": "Brother", "brothers": "Brother",
    "sister": "Sister", "sisters": "Sister",
    "nephew": "Nephew", "nephews": "Nephew",
    "niece": "Niece", "nieces": "Niece",
    "uncle": "Uncle", "uncles": "Uncle",
    "aunt": "Aunt", "aunts": "Aunt",
    "cousin": "Cousin", "cousins": "Cousin",
    "friend": "Friend", "friends": "Friend",
    "colleague": "Colleague", "colleagues": "Colleague",
    "student": "Student", "students": "Student",
    "neighbour": "Neighbour", "neighbor": "Neighbour",
    "neighbours": "Neighbour", "neighbors": "Neighbour",
}


def _contains_phrase(text: str, phrase: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(phrase.lower()) + r"(?!\w)", text) is not None


def _anniversary_in_year(dob, year: int) -> date:
    try:
        return date(year, dob.month, dob.day)
    except ValueError:  # 29 Feb in non-leap year
        return date(year, 2, 28)


def next_birthday(dob, today: date) -> date:
    candidate = _anniversary_in_year(dob, today.year)
    if candidate < today:
        candidate = _anniversary_in_year(dob, today.year + 1)
    return candidate


def _format_people(rows: pd.DataFrame, today: date, include_place=False) -> str:
    if rows.empty:
        return "No matching people were found."

    lines = []
    for _, r in rows.iterrows():
        dob = r["DOB"].date()
        nb = next_birthday(dob, today)
        days = (nb - today).days
        timing = "today" if days == 0 else ("tomorrow" if days == 1 else f"in {days} days")
        line = f"• {r['Name']} — {dob.strftime('%d %B')} ({r['Relationship']}; {timing})"
        if include_place:
            line += f" — {r['Place_of_Stay']}"
        lines.append(line)
    return "\n".join(lines)


def _find_named_person(df: pd.DataFrame, text: str):
    """Return one exact-ish person match. Full name takes precedence over nickname."""
    matches = []
    for idx, r in df.iterrows():
        full = r["Name"].lower()
        nick = r["Nickname"].lower()
        if full and _contains_phrase(text, full):
            return idx
        if nick and len(nick) >= 3 and _contains_phrase(text, nick):
            matches.append(idx)
    return matches[0] if len(matches) == 1 else None


def _relationship_filter(df: pd.DataFrame, text: str):
    for alias in sorted(RELATIONSHIP_ALIASES, key=len, reverse=True):
        if _contains_phrase(text, alias):
            canonical = RELATIONSHIP_ALIASES[alias]
            return df[df["Relationship"].str.casefold() == canonical.casefold()], canonical
    return df, None


def _month_from_text(text: str, today: date):
    if "next month" in text:
        return (today.month % 12) + 1, "next month"
    if "this month" in text:
        return today.month, "this month"
    for name, num in MONTHS.items():
        if _contains_phrase(text, name):
            return num, calendar.month_name[num]
    return None, None


def _date_window(text: str, today: date):
    """Return (start, end, human_label) for common temporal expressions."""
    if _contains_phrase(text, "today"):
        return today, today, "today"
    if _contains_phrase(text, "tomorrow"):
        t = today + timedelta(days=1)
        return t, t, "tomorrow"
    if "next 7 days" in text or "coming 7 days" in text:
        return today, today + timedelta(days=7), "the next 7 days"
    if "next 30 days" in text or "upcoming" in text or "coming birthdays" in text:
        return today, today + timedelta(days=30), "the next 30 days"
    if "this week" in text:
        end = today + timedelta(days=(6 - today.weekday()))
        return today, end, "the rest of this week"
    if "next week" in text:
        start = today + timedelta(days=(7 - today.weekday()))
        end = start + timedelta(days=6)
        return start, end, "next week"
    return None


def _rows_in_date_window(df: pd.DataFrame, start: date, end: date):
    selected = []
    # consider birthdays in both relevant calendar years
    for idx, r in df.iterrows():
        dob = r["DOB"].date()
        candidates = [_anniversary_in_year(dob, start.year)]
        if end.year != start.year:
            candidates.append(_anniversary_in_year(dob, end.year))
        if any(start <= c <= end for c in candidates):
            selected.append(idx)
    return df.loc[selected].copy()


def _sort_by_next_birthday(df: pd.DataFrame, today: date):
    if df.empty:
        return df
    out = df.copy()
    out["_next"] = out["DOB"].apply(lambda x: next_birthday(x.date(), today))
    return out.sort_values(["_next", "Name"]).drop(columns=["_next"])


def answer_question(df: pd.DataFrame, question: str, today: date | None = None):
    """Deterministic V1 rule engine.

    Returns a dict with answer + transparent trace so students can inspect
    which rules fired. No LLM or ML is used.
    """
    today = today or date.today()
    text = re.sub(r"\s+", " ", (question or "").strip().lower())
    trace = ["V1 engine: deterministic rule matching"]

    if not text:
        return {"answer": "Please type a question.", "trace": trace}

    if text in {"help", "what can i ask", "examples"} or "what can i ask" in text:
        trace.append("Rule: help/examples")
        return {
            "answer": (
                "Try questions such as:\n"
                "• What are the upcoming birthdays?\n"
                "• How many birthdays are there next month?\n"
                "• Is there any birthday tomorrow?\n"
                "• When is my wife's birthday?\n"
                "• Any nephew birthdays in September?\n"
                "• Who has birthdays this week?\n"
                "• When is Rahul's birthday?\n"
                "• Who stays in Bengaluru?"
            ),
            "trace": trace,
        }

    # A named person is a strong clue and takes precedence.
    person_idx = _find_named_person(df, text)
    if person_idx is not None:
        r = df.loc[person_idx]
        trace.append(f"Rule: named person → {r['Name']}")
        if any(k in text for k in ["where", "stay", "live", "place"]):
            trace.append("Rule: place lookup")
            return {
                "answer": f"{r['Name']} stays in {r['Place_of_Stay']}.",
                "trace": trace,
            }
        if "age" in text or "how old" in text:
            age = today.year - r["DOB"].year - ((today.month, today.day) < (r["DOB"].month, r["DOB"].day))
            trace.append("Rule: current age calculation")
            return {
                "answer": f"{r['Name']} is {age} years old as of {today.strftime('%d %B %Y')}.",
                "trace": trace,
            }
        return {
            "answer": f"{r['Name']}'s birthday is {r['DOB'].strftime('%d %B %Y')}.",
            "trace": trace,
        }

    # Simple place listing.
    if any(k in text for k in ["stays in", "stay in", "lives in", "live in", "who stays", "who lives"]):
        for place in sorted(df["Place_of_Stay"].unique(), key=len, reverse=True):
            if place and _contains_phrase(text, place.lower()):
                rows = df[df["Place_of_Stay"].str.casefold() == place.casefold()]
                trace.extend([f"Rule: place → {place}", f"Matched rows: {len(rows)}"])
                names = "\n".join(f"• {n}" for n in rows["Name"].tolist())
                return {"answer": f"People staying in {place}:\n{names}", "trace": trace}

    work, relationship = _relationship_filter(df, text)
    if relationship:
        # The dataset can contain relationship labels shared by several records.
        # For the possessive phrase "my wife", prefer the record explicitly
        # marked as the user's spouse. This remains a transparent V1 rule.
        if relationship == "Wife" and "my wife" in text:
            spouse = work[work["Relationship_Detail"].str.casefold() == "spouse"]
            if not spouse.empty:
                work = spouse
                trace.append("Rule: possessive 'my wife' → Relationship_Detail = Spouse")
        trace.append(f"Rule: relationship → {relationship}")

    month, month_label = _month_from_text(text, today)
    if month:
        trace.append(f"Rule: month → {calendar.month_name[month]}")
        rows = work[work["DOB"].dt.month == month].copy()
        rows["_day"] = rows["DOB"].dt.day
        rows = rows.sort_values(["_day", "Name"]).drop(columns=["_day"])
        trace.append(f"Matched rows: {len(rows)}")
        if "how many" in text or "count" in text or "number of" in text:
            qualifier = f" {relationship.lower()}" if relationship else ""
            return {
                "answer": f"There are {len(rows)}{qualifier} birthdays in {calendar.month_name[month]}.",
                "trace": trace,
            }
        if rows.empty:
            qualifier = f" for relationship '{relationship}'" if relationship else ""
            return {"answer": f"No birthdays found in {calendar.month_name[month]}{qualifier}.", "trace": trace}
        return {
            "answer": f"Birthdays in {calendar.month_name[month]}:\n" + _format_people(rows, today),
            "trace": trace,
        }

    window = _date_window(text, today)
    if window:
        start, end, label = window
        trace.append(f"Rule: date window → {label} ({start} to {end})")
        rows = _rows_in_date_window(work, start, end)
        rows = _sort_by_next_birthday(rows, today)
        trace.append(f"Matched rows: {len(rows)}")
        if "how many" in text or "count" in text or "number of" in text:
            return {"answer": f"There are {len(rows)} matching birthdays in {label}.", "trace": trace}
        if rows.empty:
            return {"answer": f"No matching birthdays were found in {label}.", "trace": trace}
        return {"answer": f"Birthdays in {label}:\n" + _format_people(rows, today), "trace": trace}

    # Relationship-only birthday request, e.g. "When is my wife's birthday?"
    if relationship:
        trace.append(f"Matched rows: {len(work)}")
        if len(work) == 1:
            r = work.iloc[0]
            return {
                "answer": f"{r['Name']}'s birthday is {r['DOB'].strftime('%d %B %Y')} ({relationship}).",
                "trace": trace,
            }
        if "how many" in text or "count" in text:
            return {"answer": f"There are {len(work)} people recorded as {relationship}.", "trace": trace}
        rows = _sort_by_next_birthday(work, today)
        return {"answer": f"I found {len(rows)} people recorded as {relationship}:\n" + _format_people(rows, today), "trace": trace}

    return {
        "answer": (
            "I could not match that question to a V1 rule. "
            "Type 'examples' to see the patterns this deterministic version understands."
        ),
        "trace": trace + ["No rule matched"],
    }
