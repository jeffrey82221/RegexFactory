"""
Regex Pattern Subclasses
************************

Module for Regex pattern classes like :code:`[^abc]` or :code:`(abc)` or :code:`a|b`

"""
import typing as t
from .utils import reduce_regex_list
from .extension import Group
from regexfactory.pattern import RegexPattern, ValidPatternType

class CompositionalRegexPattern(RegexPattern):
    def __or__(self, other: RegexPattern) -> RegexPattern:
        return Or(self, other)
    
class Or(CompositionalRegexPattern):
    """
    For matching multiple patterns.
    This pattern `or` that pattern `or` that other pattern.

    .. exec_code::

        from regexfactory import Or

        patt = Or("Bob", "Alice", "Sally")

        print(patt.match("Alice"))
        print(patt.match("Bob"))
        print(patt.match("Sally"))

    """

    def __init__(
        self,
        *patterns: ValidPatternType,
    ) -> None:
        regex = "|".join(
            map(
                self.get_regex,
                (
                    Group(
                        pattern,
                        capturing=False,
                    )
                    for pattern in patterns
                ),
            )
        )
        super().__init__((regex))
        self._patterns = set(patterns)
    
    def __or__(self, other: RegexPattern) -> RegexPattern:
        if isinstance(other, Or):
            merge_mapping = dict()
            for left_pattern in self._patterns:
                for right_pattern in other._patterns:
                    if left_pattern != right_pattern:
                        union_pattern = left_pattern | right_pattern
                        if not isinstance(union_pattern, Or):
                            merge_mapping[(left_pattern, right_pattern)] = union_pattern
            regex_groups = list(self._patterns | other._patterns)
            regex_groups = reduce_regex_list(regex_groups, mapping=merge_mapping)
            patterns = sorted(regex_groups, key=str)
            return Or(*list(set(patterns)))
        else:
            return other.__or__(self)
    
    def __eq__(self, other: t.Any) -> bool:
        """
        Returns whether or not two :class:`ValidPatternType`'s have the same regex.
        Otherwise return false.
        """
        if isinstance(other, Or):
            return set(self._patterns) == set(other._patterns)
        return super().__eq__(other)

class RepeatRegexPattern(CompositionalRegexPattern):
    def __init__(self, regex: str, pattern: ValidPatternType):
        self._pattern = pattern
        super().__init__(regex)

class Optional(RepeatRegexPattern):
    """
    Matches the passed :class:`ValidPatternType` between zero and one times.
    Functions the same as :code:`Amount(pattern, 0, 1)`.
    """

    def __init__(self, pattern: ValidPatternType, greedy: bool = True) -> None:
        regex = Group(pattern, capturing=False) + "?" + ("" if greedy else "?")
        super().__init__(regex, pattern)

class Multi(RepeatRegexPattern):
    """
    Matches one or more occurences of the given :class:`ValidPatternType`.
    If given :code:`match_zero=True` to the init method it matches zero or more occurences.
    """

    def __init__(
        self,
        pattern: ValidPatternType,
        match_zero: bool = False,
        greedy: bool = True,
    ):
        suffix = "*" if match_zero else "+"
        if greedy is False:
            suffix += "?"
        regex = self.get_regex(Group(pattern, capturing=False))
        super().__init__(regex + suffix, pattern)
        
class Amount(RepeatRegexPattern):
    """
    For matching multiple occurences of a :class:`ValidPatternType`.
    You can match a specific amount of occurences only.
    You can match with a lower bound on the number of occurences of a pattern.
    Or with a lower and upper bound on the number occurences.
    You can also pass a :code:`greedy=False` keyword-argument  to :class:`Amount`,
    (default is True)
    which tells the regex compiler match as few characters as possible rather than
    the default behavior which is to match as many characters as possible.

    Best explained with an example.

    .. exec_code::

        from regexfactory import Amount, Set

        # We are using the same Pattern with different amounts.

        content = "acbccbaabbccaaca"

        specific_amount = Amount(Set(*"abc"), 2)

        lower_and_upper_bound = Amount(Set(*"abc"), 3, 5, greedy=False)

        lower_and_upper_bound_greedy = Amount(Set(*"abc"), 3, 5)

        lower_bound_only = Amount(Set(*"abc"), 5, or_more=True, greedy=False)

        print(specific_amount.findall(content))
        print(lower_and_upper_bound_greedy.findall(content))
        print(lower_and_upper_bound.findall(content))
        print(lower_bound_only.findall(content))

    """

    def __init__(
        self,
        pattern: ValidPatternType,
        i: int,
        j: t.Optional[int] = None,
        or_more: bool = False,
        greedy: bool = True,
    ) -> None:
        if j is not None:
            amount = f"{i},{j}"
        elif or_more:
            amount = f"{i},"
        else:
            amount = f"{i}"
        regex = self.get_regex(pattern) + "{" + amount + "}" + ("" if greedy else "?")
        super().__init__(regex, pattern)




