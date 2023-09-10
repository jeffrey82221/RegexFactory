from regexfactory import Set, NotSet, Range, Or
from regexfactory import ANY, WHITESPACE, NOTWHITESPACE, WORD, NOTWORD, DIGIT
from regexfactory import RegexPattern

from regexfactory import (
    ANCHOR_END,
    ANCHOR_START,
    ANY,
    DIGIT,
    NOTDIGIT, # not working 
    NOTWHITESPACE, # not working 
    NOTWORD, # not working 
    WHITESPACE,
    WORD,
)
from regexfactory import (
    Amount,
    Comment,
    Extension,
    Group,
    IfAhead,
    IfBehind,
    IfGroup,
    IfNotAhead,
    IfNotBehind,
    Multi, 
    NamedGroup,
    NamedReference,
    NumberedReference,
    NotSet,
    Optional,
    Or,
    Range,
    Set,
)


def test_examples():
    assert ANCHOR_END.examples == {''}
    assert ANCHOR_START.examples == {''}
    assert DIGIT.examples.issubset(ANY.examples)
    assert DIGIT.examples == set(map(str, range(10)))
    assert ' ' in WHITESPACE.examples
    assert '\n' in WHITESPACE.examples
    assert Amount('a', 1, 3).examples == {'a', 'aa', 'aaa'}
    assert WORD.examples & NotSet(DIGIT).examples - set('_') == Set(Range('a', 'z'), Range('A', 'Z')).examples
    assert Or(DIGIT, Amount('a', 1, 3)).examples == DIGIT.examples | Amount('a', 1, 3).examples
    assert Optional('a').examples == set(['', 'a'])
    assert Comment('hello').examples == {''}
    assert RegexPattern('.').examples == ANY.examples