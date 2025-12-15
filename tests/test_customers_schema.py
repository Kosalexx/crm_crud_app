from typing import Any
from src.schemas.customers import CustomerGetSchema


def test_parse_phones_from_list_of_dicts() -> None:
    """Ensure phone numbers are parsed from a list of dicts into strings."""
    payload: dict[str, Any] = {
        "id": 1,
        "firstName": "John",
        "phones": [{"number": "123"}, {"number": "456"}],
    }
    c = CustomerGetSchema(**payload)
    assert c.phones == ["123", "456"]


def test_parse_phones_from_list_of_strings() -> None:
    """Ensure phone numbers are preserved when provided as strings."""
    payload: dict[str, Any] = {"id": 1, "firstName": "John", "phones": ["123", "456"]}
    c = CustomerGetSchema(**payload)
    assert c.phones == ["123", "456"]


def test_parse_phones_none() -> None:
    """Ensure that None phones remain None."""
    payload: dict[str, Any] = {"id": 1, "firstName": "John", "phones": None}
    c = CustomerGetSchema(**payload)
    assert c.phones is None
