"""
TODO:
- [ ] Enable union operation between CharRegexPattern and Amount{1}
"""
from regexfactory import Set, NotSet, Range, Or
from regexfactory import WORD, DIGIT, ANY
from regexfactory import Amount, Multi, Optional
from regexfactory import RegexPattern
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
    assert Amount('a', 0, 7) | Amount('a', 4, 8) == Amount('a', 0, 8)
    assert Amount('a', 2, 7) | Multi('a', match_zero=True) == Multi('a', match_zero=True)
    assert Amount('a', 1, 7) | Optional('a') == Amount('a', 0, 7)
    assert Multi('a', match_zero=True) | Optional('a') == Multi('a', match_zero=True)
    assert Multi('a', match_zero=False) | Optional('a') == Multi('a', match_zero=True)
    assert Optional('a') | Optional('a') == Optional('a')
    assert Optional(Set(*'a')) | Optional(Set(*'b')) == Optional(Set(*['a', 'b']))
    assert Amount(Set('a'), 1) | Amount(Set('b'), 1) == Set(*'ab')
    assert Amount(Set('a'), 0, 1) | Amount(Set('b'), 0, 1) == Optional(Set(*'ab'))
    assert Amount(Set('a'), 0, 1) | Amount(Set('b'), 1) == Optional(Set(*'ab'))
    assert Amount(Set('a'), 1, 3) | Multi(Set(*'ab'), match_zero=True) == Multi(Set(*'ab'), match_zero=True)
    assert Multi(Set('a')) | Amount(Set(*'ab'), 1, or_more=True) == Multi(Set(*'ab')) 
    assert Amount('a', 4, 6) | Optional('a') == Or(Amount('a', 4, 6), Optional('a'))
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
