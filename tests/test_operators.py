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

def test_group_consecutive():
    assert CharRegexPattern._group_consecutive([1,3,5]) == [[1], [3], [5]]
    assert CharRegexPattern._group_consecutive([1,2,3]) == [[1,2,3]]
    assert CharRegexPattern._group_consecutive([1,2,3,5,6]) == [[1,2,3], [5,6]]
    
def test_find_merged_regex():
    assert CharRegexPattern._find_merged_regex([Range('0', '5'), Range('4', '9'), Range('a', 'd')]) == {
        tuple([Range('0', '5'), Range('4', '9')]): DIGIT
    }
    assert CharRegexPattern._find_merged_regex([Range('0', '5'), Range('4', '9'), Range('3', '7'), Range('a', 'd')]) == {
        tuple([Range('0', '5'), Range('4', '9'), Range('3', '7')]): DIGIT,
    }
    assert CharRegexPattern._find_merged_regex([Range('0', '5'), Range('4', '9'), Range('3', '7'), WORD, Set('\n')]) == {
        tuple([Range('0', '5'), Range('4', '9'), Range('3', '7'), WORD]): WORD
    }

def test_match_special_chars():
    assert SpecialCharRegexPattern.match_special_char_regex(
        ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    ) == DIGIT
    assert SpecialCharRegexPattern.match_special_char_regex(
        ['0', '1', '2', '3', '4']
    ) == None

def test_combination_generate():
    results = []
    for e in CharRegexPattern._combination_generate([1,2,3]):
        results.append(e)
    assert results == [(1,2), (1,3), (2, 3), (1,), (2,), (3,), ]