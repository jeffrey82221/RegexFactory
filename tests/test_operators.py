"""
TODO:
- [X] Enable union operation between CharRegexPattern and Amount{1}
"""
from regexfactory import Set, NotSet, Range, Or
from regexfactory import WORD, DIGIT, ANY
from regexfactory import Amount, Multi, Optional
from regexfactory.chars import CharRegexPattern
from regexfactory import RegexPattern
def test_or_for_char_regex():
    assert Range('0', '4') | Range('3', '9') == DIGIT
    assert (Set('1') | Set('2')).regex == '[12]'
    assert (Range('0', '4') | Amount('2', 1, 2)).regex == Or(Range('0', '4'), Amount('2', 1, 2))
    assert Range('0', '5') | WORD == WORD
    assert DIGIT | WORD == WORD
    assert Range('0', '4') | Range('7', '9') == Or(Range('0', '4'), Range('7', '9'))
    assert Range('4', '7') | (Range('0', '4') | Range('7', '9')) == DIGIT 
    assert NotSet('a') | NotSet('b') == ANY
    assert CharRegexPattern('1') | CharRegexPattern('3') == Set(*'13')
    assert CharRegexPattern('1') | CharRegexPattern('3') | CharRegexPattern('2') == Range('1', '3')
    assert CharRegexPattern('1') | CharRegexPattern('1') == CharRegexPattern('1')
    assert CharRegexPattern('1') | Amount('1', 1) == CharRegexPattern('1')
    assert Amount('1', 1) | CharRegexPattern('1') == CharRegexPattern('1')
    assert Amount('1', 1) | RegexPattern('1') == CharRegexPattern('1')
    assert Amount('1', 1) | CharRegexPattern('2') == Set(*'12')
    assert Amount('1', 1) | CharRegexPattern('2') | RegexPattern('3') == Range('1', '3')
    assert Range('0', '3') | Range('5', '9') | CharRegexPattern('4') == DIGIT

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
    assert Optional('a') | Multi('a', match_zero=False) == Multi('a', match_zero=True)
    assert Multi(Set('a')) | Amount(Set(*'ab'), 1, or_more=True) == Multi(Set(*'ab')) 
    assert Amount('a', 4, 6) | Optional('a') == Or(Amount('a', 4, 6), Optional('a'))
    assert Amount('12', 1) | RegexPattern('12') == RegexPattern('12')
    assert RegexPattern('12') | Amount('12', 1) == RegexPattern('12')
    assert Amount('a', 2, 4) | Amount('a', 4, 7) == Amount('a', 2, 7)
    assert isinstance(Amount('a', 2, 4) | Amount('a', 6, 8), Or) 
    assert (Amount('a', 2, 4) | Amount('a', 6, 8))== Or(Amount('a', 2, 4), Amount('a', 6, 8))
    assert Amount('a', 2, 4) | Amount('a', 6, 8) | Amount('a', 4, 6) == Amount('a', 2, 8)
    assert Or(Amount('a', 2, 4), Amount('a', 6, 8), Range('a', 'z')) | Amount('a', 4, 6) == Amount('a', 2, 8) | Range('a', 'z')
    assert Optional('a') | Amount('a', 3) == Or(Optional('a'), Amount('a', 3))
    assert Optional('a') | Amount('a', 2) == Amount('a', 0, 2)
    assert Optional('a') | Amount('a', 2, 4) == Amount('a', 0, 4)
    assert Optional('a') | Amount('a', 2, or_more=True) == Multi('a', match_zero=True)
    assert sorted([Optional('a'), Amount('a', 5, or_more=True), Amount('a', 1, 5) ]) == [Optional('a'), Amount('a', 1, 5), Amount('a', 5, or_more=True)]
    assert Optional('a') | Amount('a', 5, or_more=True) | Amount('a', 1, 5) == Multi('a', match_zero=True)
    assert Optional('a') | Amount('a', 5, or_more=True) | Amount('b', 1, 5) == Or(Optional('a'), Amount('a', 5, or_more=True), Amount('b', 1, 5))
    assert Optional(CharRegexPattern('a')) | Optional(CharRegexPattern('b')) == Optional(Set(*'ab'))
    assert Optional('a') | Optional('b') == Optional(Set(*'ab'))
    assert Optional(RegexPattern('a')) | Optional(RegexPattern('b')) == Optional(Set(*'ab'))
    assert Amount('a', 1, 2) | RegexPattern('a') == Amount('a', 1, 2)
    assert Optional('a') | Amount('b', 1) == Optional(Set(*'ab'))
    assert Optional('a') | CharRegexPattern('a') == Optional('a')
    assert Optional('a') | RegexPattern('a') == Optional('a')
    assert Optional('a') | CharRegexPattern('b') == Optional(Set(*'ab'))
    assert Amount('a', 1, 2) | RegexPattern('a') == Amount('a', 1, 2)
    assert Optional('a') | Optional('ab') == Optional(Or('a', 'ab'))

    

def test_or_for_simple_cases():
    assert RegexPattern('123') | RegexPattern('123') == RegexPattern('123')
    assert RegexPattern('123') | RegexPattern('456') == Or(RegexPattern('123'), RegexPattern('456'))
    assert RegexPattern('1') | CharRegexPattern('1') == CharRegexPattern('1')
    assert RegexPattern('1') | CharRegexPattern('3') == Set(*'13')

def test_lt_operator():
    assert Optional('a') < Amount('a', 1)
    assert Optional('a') < Amount('a', 2)
    assert Amount('a', 3) < Multi('a')
    assert Amount('a', 2) < Amount('a', 3)
