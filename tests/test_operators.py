"""
TODO:
- [ ] Enable union operation between CharRegexPattern and Amount{1}
"""
from regexfactory import Set, NotSet, Range, Or
from regexfactory import WORD, DIGIT, ANY
from regexfactory import Amount
from regexfactory.chars import CharRegexPattern, SpecialCharRegexPattern

def test_or_for_char_regex():
    assert Range('0', '4') | Range('3', '9') == DIGIT
    assert (Set('1') | Set('2')).regex == '[12]'
    assert (Range('0', '4') | Amount('2', 1, 2)).regex == Or(Range('0', '4'), Amount('2', 1, 2))
    assert Range('0', '5') | WORD == WORD
    assert DIGIT | WORD == WORD
    assert Range('0', '4') | Range('7', '9') == Or(Range('0', '4'), Range('7', '9'))
    assert Range('4', '7') | (Range('0', '4') | Range('7', '9')) == DIGIT 
    assert NotSet('a') | NotSet('b') == ANY

def test_or_for_compositional_regex():
    assert Or(Range('1', '4'), Set(*['a', 'b'])) | Set(*['a', 'b']) == Or(Range('1', '4'), Set(*['a', 'b']))
    assert Or(Amount('a', 2), Amount('b', 4)).__or__(Or(Amount('b', 4), Amount('c', 3)))  == Or(Amount('a', 2), Amount('b', 4), Amount('c', 3))
    assert Or(Range('1', '4'), Set(*['a', 'b'])) | Or(Range('1', '4'), Set(*['a', 'b']))  == Or(Range('1', '4'), Set(*['a', 'b']))
    assert Or(Range('1', '4')) | Or(Set(*['a', 'b']))  == Or(Range('1', '4'), Set(*['a', 'b']))
    assert Or(Range('1', '4')) | Or(Set(*['a', 'b']), Amount('3', 3))  == Or(Range('1', '4'), Set(*['a', 'b']), Amount('3', 3))
    assert Or(Amount('a', 2), Range('0', '5')) | Or(Amount('b', 3), Range('5', '9')) == Or(Amount('a', 2), Amount('b', 3), DIGIT)


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
