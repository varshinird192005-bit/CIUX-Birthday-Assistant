from service import load_people, execute
from nlu import parse

def test_dataset_has_100_records():
    assert len(load_people()) == 100

def test_relationship_month_query_is_grounded():
    people = load_people()
    parsed = parse("Any nephew birthdays in September?", people)
    assert parsed["entities"]["relationship"] == "Nephew"
    assert parsed["entities"]["month"] == 9
    answer = execute(parsed, people)
    assert "September" not in answer or "No matching" in answer or "—" in answer

def test_named_person_is_resolved():
    people = load_people()
    parsed = parse("When is Rahul Patil's birthday?", people)
    assert parsed["entities"]["person_id"] == "P004"
    assert "18 September 2004" in execute(parsed, people)
