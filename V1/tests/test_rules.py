from datetime import date
from data_service import load_people
from rules import answer_question

DF = load_people()
TODAY = date(2026, 9, 11)


def ask(q):
    return answer_question(DF, q, today=TODAY)["answer"]


def test_named_person_birthday():
    text = ask("When is Rahul Patil's birthday?")
    assert "18 September 2004" in text


def test_wife_birthday():
    text = ask("When is my wife's birthday?")
    assert "Lakshmi Rao" in text
    assert "14 December 1982" in text


def test_nephew_september():
    text = ask("Any nephew birthdays in September?")
    assert "Rahul Patil" in text
    assert "Nikhil Hegde" not in text


def test_tomorrow_is_deterministic():
    text = ask("Is there any birthday tomorrow?")
    assert isinstance(text, str) and len(text) > 0


def test_place_lookup():
    text = ask("Who stays in Bengaluru?")
    assert "People staying in Bengaluru" in text


def test_unknown_rule():
    text = ask("Tell me something poetic")
    assert "could not match" in text.lower()
