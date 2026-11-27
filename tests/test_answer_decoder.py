
import pytest

from scanner.answer_decoder import decode_answer


@pytest.mark.parametrize(
    "direction, expected",
    [
        ("TOP", "A"),
        ("RIGHT", "B"),
        ("BOTTOM", "C"),
        ("LEFT", "D"),
    ]
)
def test_answer_orientation(direction, expected):

    assert decode_answer(direction) == expected


def test_invalid_direction():

    with pytest.raises(ValueError):
        decode_answer("DIAGONAL")


def test_lowercase_direction():

    assert decode_answer("top") == "A"


def test_all_four_options_are_unique():

    answers = [
        decode_answer("TOP"),
        decode_answer("RIGHT"),
        decode_answer("BOTTOM"),
        decode_answer("LEFT")
    ]

    assert len(set(answers)) == 4
