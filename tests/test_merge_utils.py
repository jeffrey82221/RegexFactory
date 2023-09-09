from regexfactory.utils import _combination_generate, find_merge_ways
from regexfactory import Range, DIGIT, WORD, Set
from regexfactory.chars import SpecialCharRegexPattern
def test_combination_generate():
    results = []
    for e in _combination_generate([1,2,3]):
        results.append(e)
    assert results == [(1,2), (1,3), (2, 3), (1,), (2,), (3,), ]


    
def test_find_merge_ways():
    assert find_merge_ways([Range('0', '5'), Range('4', '9'), Range('a', 'd')], example_inference_callable=SpecialCharRegexPattern.match_special_char_regex) == {
        tuple([Range('0', '5'), Range('4', '9')]): DIGIT
    }
    assert find_merge_ways([Range('0', '5'), Range('4', '9'), Range('3', '7'), Range('a', 'd')], example_inference_callable=SpecialCharRegexPattern.match_special_char_regex) == {
        tuple([Range('0', '5'), Range('4', '9'), Range('3', '7')]): DIGIT,
    }
    assert find_merge_ways([Range('0', '5'), Range('4', '9'), Range('3', '7'), WORD, Set('\n')], example_inference_callable=SpecialCharRegexPattern.match_special_char_regex) == {
        tuple([Range('0', '5'), Range('4', '9'), Range('3', '7'), WORD]): WORD
    }