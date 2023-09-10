"""
Regex Pattern Subclasses
************************

Module for Regex pattern classes like :code:`[^abc]` or :code:`(abc)` or :code:`a|b`

"""
from functools import reduce
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
        try:
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
        except BaseException as e:
            msg = f'input: {patterns}'
            raise ValueError(msg) from e
        super().__init__((regex))
        self._patterns = set(map(RegexPattern.convert_to_regex_pattern, patterns))
    
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
    
    def __hash__(self):
        result = hash('Or')
        for pattern in self._patterns:
            result += pattern.__hash__()
        return result

class OccurrenceRegexPattern(CompositionalRegexPattern):
    def __init__(self, regex: str, pattern: ValidPatternType):
        pattern = RegexPattern.convert_to_regex_pattern(pattern)
        from regexfactory.chars import CharRegexPattern
        try:
            examples = pattern.examples
        except BaseException as e:
            raise ValueError(f'error getting examples for pattern {pattern} of type {type(pattern)}') from e
        try:
            if ex:=CharRegexPattern.match_char_regex(examples):
                pattern = ex
        except BaseException as e:
            raise ValueError(f'error match_char_regex for examples: {examples}') from e

        
        self._pattern = pattern
        assert isinstance(self._pattern, RegexPattern)
        super().__init__(regex)
        

    def __lt__(self, other: 'OccurrenceRegexPattern') -> bool:
        assert self._pattern == other._pattern, 'pattern should be the same for < operation between two OccurrenceRegexPattern'
        if type(self) == type(other):
            if isinstance(self, Multi):
                if self._match_zero and not other._match_zero:
                    return True
            elif isinstance(self, Amount):
                if other._or_more and not self._or_more:
                    return True
                if self._i < other._i:
                    return True
        else:
            if isinstance(self, Optional):
                return True
            elif isinstance(self, Amount) and isinstance(other, Optional):
                return False
            elif isinstance(self, Amount) and isinstance(other, Multi):
                return True
            elif isinstance(self, Multi):
                return False
        return False
    
    def __or__(self, other: Or) -> CompositionalRegexPattern:
        assert isinstance(other, Or), 'OccurrenceRegexPattern only implements __or__ for `Or` on the right.'
        patterns = set(list(other._patterns) + [self])
        def is_target(pattern):
            return isinstance(pattern, OccurrenceRegexPattern) and pattern._pattern == self._pattern
        target_patterns = list(filter(is_target, patterns))
        non_target_patterns = list(patterns - set(target_patterns))        
        reduced_pattern = reduce(lambda x,y: x|y, sorted(target_patterns))
        if non_target_patterns:
            if isinstance(reduced_pattern, OccurrenceRegexPattern):
                result_patterns = non_target_patterns + [reduced_pattern]
            elif isinstance(reduced_pattern, Or):
                result_patterns = non_target_patterns + reduced_pattern._patterns
            return Or(*list(set(result_patterns)))
        else:
            return reduced_pattern


    
class Optional(OccurrenceRegexPattern):
    """
    Matches the passed :class:`ValidPatternType` between zero and one times.
    Functions the same as :code:`Amount(pattern, 0, 1)`.
    """

    def __init__(self, pattern: ValidPatternType, greedy: bool = True) -> None:
        regex = Group(pattern, capturing=False) + "?" + ("" if greedy else "?")
        super().__init__(regex, pattern)

    def __or__(self, other: RegexPattern) -> RegexPattern:
        from regexfactory.chars import CharRegexPattern
        if isinstance(other, Or):
            return super().__or__(other)
        elif isinstance(other, Optional):
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
                if not other._or_more and isinstance(other._j, int):
                    if other._j < 2:
                        return self
                    elif other._i <= 2:
                        return Amount(self._pattern, 0, other._j)
                elif not other._or_more and not isinstance(other._j, int):
                    if other._i < 2:
                        return self
                    elif other._i == 2:
                        return Amount(self._pattern, 0, 2)
                else: 
                    if other._i <= 2:
                        return Multi(self._pattern, match_zero=True)
            else:
                # When Occurrence of Amount same as Optional:
                if other._i == 0 and other._j == 1 and not other._or_more:
                    return Optional(self._pattern|other._pattern)
                elif other._i == 1 and other._j is None and not other._or_more:
                    return Optional(self._pattern|other._pattern)
        elif type(other) in [RegexPattern, CharRegexPattern]:
            if self._pattern == other:
                return self
            else:
                return Optional(self._pattern | other)
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
        if isinstance(other, Or):
            return super().__or__(other)
        elif isinstance(other, Optional):
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
        from regexfactory.chars import CharRegexPattern        
        if isinstance(other, Or):
            return super().__or__(other)
        elif isinstance(other, CharRegexPattern):
            return other.__or__(self)
        elif isinstance(other, Optional):
            return other.__or__(self)
        elif isinstance(other, Multi):
            return other.__or__(self)
        elif isinstance(other, Amount):
            if self._pattern == other._pattern:
                if self._j is not None:
                    if other._j is not None:
                        # self (i, ..., j)
                        # other (i, ..., j)
                        if len(set(range(self._i, self._j + 1)) & set(range(other._i, other._j + 1))):
                            return Amount(self._pattern, min(self._i, other._i), j=max(self._j, other._j))
                    elif other._or_more:
                        # self (i, ... j)
                        # other (i, ...)
                        if other._i <= self._j:
                            result = Amount(self._pattern, min(self._i, other._i), or_more=True)
                            if result.is_multi:
                                return result.to_multi()
                            else:
                                return result
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
                            result = Amount(self._pattern, min(self._i, other._i), or_more=True)
                            if result.is_multi:
                                return result.to_multi()
                            else:
                                return result
                    elif other._or_more:
                        # self (i, ...)
                        # other (i, ...)
                        result = Amount(self._pattern, min(self._i, other._i), or_more=True)
                        if result.is_multi:
                            return result.to_multi()
                        else:
                            return result
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
                            if other.is_multi:
                                return other.to_multi()
                            else:
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
        elif isinstance(other, RegexPattern):
            if self._is_simple and self._pattern == other:
                return other
            elif not self._is_simple and self._pattern == other:
                return self | Amount(other, 1)
        
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