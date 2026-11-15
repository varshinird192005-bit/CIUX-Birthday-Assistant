
import calendar
import re

MONTHS = {
    m.lower(): i
    for i, m in enumerate(calendar.month_name)
    if m
}


def parse(message, people):
    text = (message or '').lower().strip()

    result = {
        'intent': 'unknown',
        'entities': {}
    }

    e = result['entities']

    if not text:
        return result

    # 1. Intent classification
    if 'how many' in text or 'count' in text or 'number of' in text:
        result['intent'] = 'count_birthdays'

    elif 'where' in text or 'stay' in text or 'live' in text:
        result['intent'] = 'person_place'

    elif 'upcoming' in text or 'coming birthdays' in text:
        result['intent'] = 'upcoming_birthdays'

    else:
        result['intent'] = 'birthday_search'

    # 2. Relative date extraction
    if 'tomorrow' in text:
        e['relative_date'] = 'tomorrow'

    # 3. Relative month extraction
    if 'next month' in text:
        e['relative_month'] = 'next'

    # 4. Month extraction
    for name, number in MONTHS.items():
        if re.search(r'\b' + name + r'\b', text):
            e['month'] = number
            break

    # 5. Relationship extraction from Excel
    for rel in sorted(
        people['Relationship'].dropna().unique(),
        key=len,
        reverse=True
    ):
        token = str(rel).lower()

        if re.search(
            r'\b' + re.escape(token) + r's?\b',
            text
        ):
            e['relationship'] = rel
            break

    # 6. Person name and nickname extraction
    for _, row in people.iterrows():

        candidates = [
            str(row['Name']),
            str(row.get('Nickname', ''))
        ]

        for candidate in candidates:
            candidate = candidate.lower().strip()

            if candidate and candidate != 'nan':
                if re.search(
                    r'\b' + re.escape(candidate) + r'\b',
                    text
                ):
                    e['person_id'] = str(row['Person_ID'])
                    e['person_name'] = row['Name']
                    break

        if 'person_id' in e:
            break

    return result
