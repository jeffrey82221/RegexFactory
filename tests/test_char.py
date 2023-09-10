import pytest
from regexfactory import RegexPattern, Amount
from regexfactory.chars import CharRegexPattern, SpecialCharRegexPattern
from regexfactory import DIGIT, Range, ANY
import re
def test_match_special_chars():
    assert SpecialCharRegexPattern.match_special_char_regex(
        ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    ) == DIGIT
    assert SpecialCharRegexPattern.match_special_char_regex(
        ['0', '1', '2', '3', '4']
    ) == None

def test_is_chars():
    assert CharRegexPattern.is_char(DIGIT.regex)
    assert CharRegexPattern.is_char(Amount('a', 1).regex)
    assert CharRegexPattern.is_char(RegexPattern('\w').regex)
    assert CharRegexPattern.is_char(ANY.regex)
    assert CharRegexPattern.is_char(Range('1', '3').regex)
