import pytest
from regexfactory import RegexPattern, Amount
from regexfactory.chars import CharRegexPattern, SpecialCharRegexPattern
from regexfactory import DIGIT, Range
import re
def test_match_special_chars():
    assert SpecialCharRegexPattern.match_special_char_regex(
        ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    ) == DIGIT
    assert SpecialCharRegexPattern.match_special_char_regex(
        ['0', '1', '2', '3', '4']
    ) == None

def test_match_single_chars():
    assert CharRegexPattern.match_char_regex(
        ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    ) == DIGIT
    assert CharRegexPattern.match_char_regex(
        ['3', '4', '5', '6']
    ) == Range('3', '6')

def test_convert_to_char_regex():
    assert CharRegexPattern.convert_to_char_regex('1') == CharRegexPattern('1')
    assert CharRegexPattern.convert_to_char_regex(re.compile('1')) == CharRegexPattern('1')
    assert CharRegexPattern.convert_to_char_regex(CharRegexPattern('1')) == CharRegexPattern('1')
    assert CharRegexPattern.convert_to_char_regex(RegexPattern('1')) == CharRegexPattern('1')
    with pytest.raises(AssertionError):
        CharRegexPattern.convert_to_char_regex(RegexPattern('12'))
    with pytest.raises(AssertionError):
        CharRegexPattern.convert_to_char_regex('12')
    with pytest.raises(AssertionError):
        CharRegexPattern.convert_to_char_regex(Amount('a', 2))