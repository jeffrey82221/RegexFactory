from regexfactory.patterns import RegexPattern
from regexfactory.chars import CharRegexPattern
from regexfactory.pattern import LongRegexPattern
from regexfactory import DIGIT, Amount, Optional, Multi

def test_add():
    assert isinstance(RegexPattern('a') + RegexPattern('b'), LongRegexPattern)
    assert RegexPattern('a') + RegexPattern('b') == LongRegexPattern(
        *[CharRegexPattern('a'), CharRegexPattern('b')]
    )
    assert RegexPattern('a') + RegexPattern('c') == LongRegexPattern(
        *[CharRegexPattern('a'), CharRegexPattern('c')]
    )
    assert RegexPattern('a') + RegexPattern('b') + RegexPattern('c') == LongRegexPattern(
        *[CharRegexPattern('a'), CharRegexPattern('b'), CharRegexPattern('c')]
    )
    assert RegexPattern('a') + LongRegexPattern(*[
        CharRegexPattern('b'), CharRegexPattern('c')
    ]) == LongRegexPattern(
        *[CharRegexPattern('a'), CharRegexPattern('b'), CharRegexPattern('c')]
    )
    assert DIGIT + LongRegexPattern(*[
        CharRegexPattern('b'), CharRegexPattern('c')
    ]) == LongRegexPattern(
        *[DIGIT, CharRegexPattern('b'), CharRegexPattern('c')]
    )
    assert DIGIT + DIGIT == Amount(DIGIT, 2)
    assert DIGIT + DIGIT + DIGIT == Amount(DIGIT, 3)
    assert Amount(DIGIT, 2) + Amount(DIGIT, 3) == Amount(DIGIT, 5)
    assert DIGIT + Multi(DIGIT, match_zero=True) == Multi(DIGIT, match_zero=False)
    assert DIGIT + Multi(DIGIT, match_zero=False) == Amount(DIGIT, 2, or_more=True)
    assert Multi(DIGIT, match_zero=False) + DIGIT == Amount(DIGIT, 2, or_more=True)
    assert Multi(DIGIT, match_zero=False) + Optional(DIGIT) == Multi(DIGIT, match_zero=False)
    assert Optional(DIGIT) + Multi(DIGIT, match_zero=True) == Multi(DIGIT, match_zero=True)
    assert Optional(DIGIT) + Amount(DIGIT, 3, 5) == Amount(DIGIT, 3, 6)
    assert Optional(DIGIT) + Amount(DIGIT, 3, or_more=True) == Amount(DIGIT, 3, or_more=True)
    assert Optional(DIGIT) + Amount(DIGIT, 3) == Amount(DIGIT, 3, j=4)
    assert Amount(DIGIT, 0, or_more=True) + Amount(DIGIT, 3) == Amount(DIGIT, 3, or_more=True)
    assert Amount(DIGIT, 3) + Amount(DIGIT, 0, or_more=True)  == Amount(DIGIT, 3, or_more=True)
    assert Amount(DIGIT, 3) + Amount(DIGIT, 5, or_more=True)  == Amount(DIGIT, 8, or_more=True)
    assert Amount(DIGIT, 0, or_more=True) + Amount(DIGIT, 3) == Amount(DIGIT, 3, or_more=True)
    assert Amount(DIGIT, 5, or_more=True) + Amount(DIGIT, 3) == Amount(DIGIT, 8, or_more=True)
    assert Multi(DIGIT, match_zero=True) + Amount(DIGIT, 3)   == Amount(DIGIT, 3, or_more=True)
    assert Multi(DIGIT, match_zero=False) + Amount(DIGIT, 3)   == Amount(DIGIT, 4, or_more=True)
    assert CharRegexPattern('a') + CharRegexPattern('a') == Amount(CharRegexPattern('a'), 2)
    assert CharRegexPattern('b') + CharRegexPattern('a') + CharRegexPattern('a') == LongRegexPattern(
        *[CharRegexPattern('b'), Amount(CharRegexPattern('a'), 2)])
    
    assert CharRegexPattern('a') + CharRegexPattern('a') + CharRegexPattern('a') == Amount(CharRegexPattern('a'), 3)
    assert LongRegexPattern(
        *[CharRegexPattern('a'), CharRegexPattern('b')]) + LongRegexPattern(
        *[CharRegexPattern('a'), CharRegexPattern('b')]) == Amount(
            LongRegexPattern(*[CharRegexPattern('a'), CharRegexPattern('b')]), 2)
    assert LongRegexPattern(
        *[CharRegexPattern('a'), CharRegexPattern('b')]) + LongRegexPattern(
        *[CharRegexPattern('b'), CharRegexPattern('c')])  == LongRegexPattern(*[
            CharRegexPattern('a'), Amount(CharRegexPattern('b'), 2), CharRegexPattern('c')
        ])