import pytest

from regexfactory import Range


@pytest.mark.patterns
def test_numeric_range():
    start = "0"
    end = "9"
    assert Range(start, end).regex == "[0-9]"


@pytest.mark.patterns
@pytest.mark.parametrize(
    "start, stop, expected",
    [
        ("0", "9", "[0-9]"),
        ("a", "f", "[a-f]"),
        ("r", "q", "[r-q]"),
        ("A", "Z", "[A-Z]"),
    ],
)
def test_range_parameters(start, stop, expected):
    actual = Range(start=start, stop=stop)
    assert actual.regex == expected

def test_group_consecutive():
    assert Range._group_consecutive([1,3,5]) == [[1], [3], [5]]
    assert Range._group_consecutive([1,2,3]) == [[1,2,3]]
    assert Range._group_consecutive([1,2,3,5,6]) == [[1,2,3], [5,6]]
