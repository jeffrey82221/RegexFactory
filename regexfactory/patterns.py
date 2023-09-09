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

class OccurrenceRegexPattern(CompositionalRegexPattern):
    def __init__(self, regex: str, pattern: ValidPatternType):
        self._pattern = pattern
        super().__init__(regex)

class Optional(OccurrenceRegexPattern):
    """
    Matches the passed :class:`ValidPatternType` between zero and one times.
    Functions the same as :code:`Amount(pattern, 0, 1)`.
    """

    def __init__(self, pattern: ValidPatternType, greedy: bool = True) -> None:
        regex = Group(pattern, capturing=False) + "?" + ("" if greedy else "?")
        super().__init__(regex, pattern)

    def __or__(self, other: RegexPattern) -> RegexPattern:
        if isinstance(other, Optional):
            if self._pattern == other._pattern:
                return self
            else:
                return Optional(self._pattern|other._pattern)
        elif isinstance(other, Multi):
            if self._pattern == other._pattern:
                return Multi(self._pattern, match_zero=True)
        elif isinstance(other, Amount):
            if self._pattern == other._pattern:
                # No gap between the occurrence count
                if other._i <= 2:
                    return Amount(self._pattern, 0, j=other._j, or_more=other._or_more)
            else:
                # When Occurrence of Amount same as Optional:
                if other._i == 0 and other._j == 1 and not other._or_more:
                    return Optional(self._pattern|other._pattern)

        return Or(self, other)
    
class Multi(OccurrenceRegexPattern):
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
        self._match_zero = match_zero
    

    def __or__(self, other: RegexPattern) -> RegexPattern:
        if isinstance(other, Optional):
            return other.__or__(self)
        elif isinstance(other, Multi):
            if self._pattern == other._pattern:
                return Multi(self._pattern, match_zero=(self._match_zero or other._match_zero))
            else:
                if other._pattern.issubset(self._pattern):
                    return Multi(self._pattern, match_zero=(self._match_zero or other._match_zero))
                if self._pattern.issubset(other._pattern):
                    return Multi(other._pattern, match_zero=(self._match_zero or other._match_zero))
        elif isinstance(other, Amount):
            if self._pattern == other._pattern:
                if self._match_zero:
                    return self
                else:
                    if other._i == 0:
                        return Multi(self._pattern, match_zero=True)
                    else:
                        return Multi(self._pattern, match_zero=False)
            else:
                # When the Occurrence of Amount is same with Multi
                if other._pattern.issubset(self._pattern):
                    if self._match_zero:
                        return self
                    else:
                        if other._i >= 1:
                            return self
                if other.is_multi:
                    return self.__or__(other.to_multi())
                    
        return Or(self, other)

class Amount(OccurrenceRegexPattern):
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
        self._i = i
        self._j = j
        self._or_more = or_more

    def __or__(self, other: RegexPattern) -> RegexPattern:
        if isinstance(other, Optional):
            return other.__or__(self)
        elif isinstance(other, Multi):
            return other.__or__(self)
        elif isinstance(other, Amount):
            if self._pattern == other._pattern:
                if self._j is not None:
                    if other._j is not None:
                        # self (i, ..., j)
                        # other (i, ..., j)
                        if other._i <= self._j or self._i <= other._j:
                            return Amount(self._pattern, min(self._i, other._i), j=max(self._j, other._j))
                    elif other._or_more:
                        # self (i, ... j)
                        # other (i, ...)
                        if other._i <= self._j:
                            return Amount(self._pattern, min(self._i, other._i), or_more=True)
                    else:
                        # self: (i, ..., j)
                        # other: (i)
                        if self._i <= other._i and other._i <= self._j:
                            return self
                        
                elif self._or_more:
                    if other._j is not None:
                        # self (i, ...)
                        # other (i, ..., j)
                        if self._i <= other._j:
                            return Amount(self._pattern, min(self._i, other._i), or_more=True)
                    elif other._or_more:
                        # self (i, ...)
                        # other (i, ...)
                        return Amount(self._pattern, min(self._i, other._i), or_more=True)
                    else:
                        # self (i, ...)
                        # other (i)
                        if other._i >= self._i:
                            return self
                else:
                    if other._j is not None:
                        # self (i)
                        # other (i, ..., j)
                        if other._i <= self._i and self._i <= other._j:
                            return other
                    elif other._or_more:
                        # self (i)
                        # other (i, ...)
                        if other._i <= self._i:
                            return other
                    else:
                        # self (i)
                        # other (i)
                        if self._i == other._i:
                            return self
            elif self._i == other._i and self._j == other._j and self._or_more == other._or_more:
                if other._pattern.issubset(self._pattern):
                    return self
                if self._pattern.issubset(other._pattern):
                    return other
                if self._is_simple and other._is_simple:
                    return self._pattern | other._pattern
                if self._is_optional and other._is_optional:
                    return Optional(self._pattern | other._pattern)
            elif (self._is_optional and other._is_simple) or (self._is_simple and other._is_optional):
                return Optional(self._pattern | other._pattern)
        return Or(self, other)
    
    @property
    def _is_simple(self) -> bool:
        if self._i == 1 and (self._j == None or self._j == 1) and not self._or_more:
            return True
        else:
            return False
    
    @property
    def _is_optional(self) -> bool:
        if self._i == 0 and self._j == 1:
            return True
        else:
            return False
    @property 
    def is_multi(self) -> bool:
        if self._or_more and self._j == None:
            if self._i == 0 or self._i == 1:
                return True
        return False
    
    def to_multi(self) -> Multi:
        assert self.is_multi
        return Multi(self._pattern, match_zero=(self._i==0))