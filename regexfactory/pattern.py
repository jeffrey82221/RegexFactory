"""
Base Pattern Module
*******************

Module for the :class:`RegexPattern` class.
"""
from typing import Set
import re
from typing import Any, Iterator, List, Optional, Tuple, Union
import exrex
#:
ValidPatternType = Union[re.Pattern, str, "RegexPattern"]

#: Special characters that need to be escaped to be used without their special meanings.
ESCAPED_CHARACTERS = "()[]{}?*+-|^$\\.&~#"


def join(*patterns: ValidPatternType) -> "RegexPattern":
    """Umbrella function for combining :class:`ValidPatternType`'s into a :class:`RegexPattern`."""
    joined = RegexPattern("")
    for pattern in patterns:
        joined += RegexPattern(pattern)
    return joined


def escape(string: str) -> "RegexPattern":
    """Escapes special characters in a string to use them without their special meanings."""
    return RegexPattern(re.escape(string))


class RegexPattern:
    """
    The main object that represents Regular Expression Pattern strings for this library.
    """

    regex: str

    def __init__(self, pattern: ValidPatternType, /) -> None:
        self.regex = self.get_regex(pattern)

    def __repr__(self) -> str:
        raw_regex = f"{self.regex!r}".replace("\\\\", "\\")
        return f"<RegexPattern {raw_regex}>"

    def __str__(self) -> str:
        return self.regex

    def __add__(self, other: ValidPatternType) -> 'LongRegexPattern':
        """Adds two :class:`ValidPatternType`'s together, into a :class:`LongRegexPattern`"""
        from regexfactory import Amount
        from regexfactory import patterns
        if isinstance(other, RegexPattern):
            if self == other:
                return Amount(self, 2)
            elif isinstance(other, patterns.OccurrenceRegexPattern) and self == other._pattern:
                if isinstance(other, patterns.Optional):
                    return Amount(self, 1, 2)
                elif isinstance(other, patterns.Multi):
                    if other._match_zero:
                        return patterns.Multi(self, match_zero=False)
                    else:
                        return patterns.Amount(self, 2, or_more=True)
                else:
                    return Amount(self, other._i + 1, j=other._j, or_more=other._or_more)
            elif isinstance(other, LongRegexPattern):
                patterns = [self] + other._patterns
                return LongRegexPattern(*patterns)
            else:
                return LongRegexPattern(*[self, other])
        else:
            try:
                other = self.get_regex(other)
            except TypeError:
                return NotImplemented

            return RegexPattern(self.regex + other)

    
    def __mul__(self, coefficient: int) -> "RegexPattern":
        """Treats :class:`RegexPattern` as a string and multiplies it by an integer."""
        assert coefficient >= 1
        from regexfactory import Amount
        if coefficient > 1:
            return Amount(self, coefficient)
        else:
            return self

    def __eq__(self, other: Any) -> bool:
        """
        Returns whether or not two :class:`ValidPatternType`'s have the same regex.
        Otherwise return false.
        """
        if isinstance(other, (str, re.Pattern, RegexPattern)):
            return self.regex == self.get_regex(other)
        return super().__eq__(other)

    def __hash__(self) -> int:
        """Hashes the regex string."""
        return hash(self.regex)

    @staticmethod
    def get_regex(obj: ValidPatternType, /) -> str:
        """
        Extracts the regex content from :class:`RegexPattern` or :class:`re.Pattern` objects
        else return the input :class:`str`.
        """
        if isinstance(obj, RegexPattern):
            return obj.regex
        if isinstance(obj, str):
            return obj
        if isinstance(obj, re.Pattern):
            return obj.pattern
        raise TypeError(f"Can't get regex from {obj.__class__.__qualname__} for object {obj}.")

    def compile(
        self,
        *,
        flags: int = 0,
    ) -> re.Pattern:
        """See :func:`re.compile`."""
        return re.compile(self.regex, flags=flags)

    def match(
        self,
        content: str,
        /,
        *,
        flags: int = 0,
    ) -> Optional[re.Match]:
        """See :meth:`re.Pattern.match`."""
        return self.compile(flags=flags).match(content)

    def fullmatch(
        self,
        content: str,
        /,
        *,
        flags: int = 0,
    ) -> Optional[re.Match]:
        """See :meth:`re.Pattern.fullmatch`."""
        return self.compile(flags=flags).fullmatch(content)

    def findall(
        self,
        content: str,
        /,
        *,
        flags: int = 0,
    ) -> List[Tuple[str, ...]]:
        """See :meth:`re.Pattern.findall`."""
        return self.compile(flags=flags).findall(content)

    def finditer(
        self,
        content: str,
        /,
        *,
        flags: int = 0,
    ) -> Iterator[re.Match]:
        """See :meth:`re.Pattern.finditer`."""
        return self.compile(flags=flags).finditer(content)

    def split(
        self,
        content: str,
        /,
        maxsplit: int = 0,
        *,
        flags: int = 0,
    ) -> List[Any]:
        """See :meth:`re.Pattern.split`."""
        return self.compile(flags=flags).split(content, maxsplit=maxsplit)

    def sub(
        self,
        replacement: str,
        content: str,
        /,
        count: int = 0,
        *,
        flags: int = 0,
    ) -> str:
        """See :meth:`re.Pattern.sub`."""
        return self.compile(flags=flags).sub(replacement, content, count=count)

    def subn(
        self,
        replacement: str,
        content: str,
        /,
        count: int = 0,
        *,
        flags: int = 0,
    ) -> Tuple[str, int]:
        """See :meth:`re.Pattern.subn`."""
        return self.compile(flags=flags).subn(replacement, content, count=count)

    def search(
        self,
        content: str,
        /,
        pos: int = 0,
        endpos: int = 0,
        *,
        flags: int = 0,
    ) -> Optional[re.Match]:
        """See :meth:`re.Pattern.search`."""
        return self.compile(flags=flags).search(content, pos, endpos)

    @property
    def examples(self) -> Set:
        try:
            return set(list(exrex.generate(str(self))))
        except re.error as e:
            msg = 'Regex: ' + str(self) + f' cannot generate examples succesfully. type(self): {type(self)}'
            raise ValueError(msg) from e

    def issubset(self, superset: 'RegexPattern') -> bool:
        return all([superset.fullmatch(x) is not None for x in self.examples])

    @staticmethod
    def convert_to_regex_pattern(pattern: ValidPatternType) -> 'RegexPattern':
        if isinstance(pattern, RegexPattern):
            result = pattern
        else:
            # get pattern in term of str
            if isinstance(pattern, re.Pattern):
                pattern = pattern.pattern
            assert isinstance(pattern, str)
            result = RegexPattern(pattern)
        return result

    def __or__(self, other: 'RegexPattern') -> 'RegexPattern':
        from regexfactory import Or
        from regexfactory.chars import CharRegexPattern
        from regexfactory.patterns import CompositionalRegexPattern
        if self == other:
            return self
        elif isinstance(other, CompositionalRegexPattern) or isinstance(other, CharRegexPattern):
            return other.__or__(self)
        else:
            return Or(self, other)


class LongRegexPattern(RegexPattern):
    def __init__(
        self,
        *patterns: ValidPatternType,
    ) -> None:
        assert len(patterns) > 1, f'LongRegexPattern should have more than 2 elements, but now patterns={patterns}'
        super_input = ''
        for pattern in patterns:
            super_input += self.get_regex(pattern)
        super().__init__((super_input))        
        self._patterns = list(patterns)

    def __add__(self, other: RegexPattern) -> RegexPattern:
        from regexfactory import Amount
        if isinstance(other, LongRegexPattern):
            if self == other:
                return Amount(self, 2)
            touch_merged = self._patterns[-1] + other._patterns[0]
            if not isinstance(touch_merged, LongRegexPattern):
                if len(self._patterns[:-1]) > 1:
                    left = LongRegexPattern(self._patterns[:-1])
                elif len(self._patterns[:-1]) == 1:
                    left = self._patterns[0]
                if len(other._patterns[1:]) > 1:
                    right = LongRegexPattern(other._patterns[1:])
                elif len(self._patterns[1:]) == 1:
                    right = other._patterns[-1]
                return left + touch_merged + right
            else:
                patterns = self._patterns + other._patterns
        else:
            touch_merged = self._patterns[-1] + other
            if not isinstance(touch_merged, LongRegexPattern):
                if len(self._patterns[:-1]) > 1:
                    left = LongRegexPattern(self._patterns[:-1])
                elif len(self._patterns[:-1]) == 1:
                    left = self._patterns[0]
                return left + touch_merged
            else:
                patterns = self._patterns + [other]
        return LongRegexPattern(*patterns)