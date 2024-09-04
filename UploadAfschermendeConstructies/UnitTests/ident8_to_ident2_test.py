import pytest


class IdentConverter:
    @classmethod
    def convert(cls, ident8: str) -> str | None:
        if not isinstance(ident8, str) or len(ident8) != 8:
            return None
        if not ident8[0].isalpha() or not ident8[1:4].isdigit():
            return None
        number = ident8[1:4].lstrip('0')
        if ident8[4] == '9':
            return f'{ident8[0]}{number}{chr(96 + int(ident8[5:7]))}'
        return f'{ident8[0]}{number}'


@pytest.mark.parametrize(
    "input_value, expected_output", [
        # Happy path tests
        ("R0010001", "R1"),
        ("R0010002", "R1"),
        ("A0020001", "A2"),
        ("A0120001", "A12"),
        ("B2010001", "B201"),
        # Edge cases
        ("R0119012", "R11a"),
        ("R0119262", "R11z"),
        # Error cases
        (None, None),  # Empty input
        (12345, None),  # Non-string input
        ('1234567', None),  # String not length 8
        ('12345678', None),  # First character not letter
        ('R12A4567', None),  # Number has alphanumeric characters
    ]
)
def test_ident_converter(input_value, expected_output):
    result = IdentConverter.convert(input_value)
    assert result == expected_output
