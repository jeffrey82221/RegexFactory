r"""
Regex Characters
*******************

Common regex special characters, such as :code:`\d`, :code:`.`, ...
More information about special characters in python regex available
`here <https://docs.python.org/3/library/re.html#regular-expression-syntax>`__
"""
from functools import reduce
from typing import Optional
from .pattern import RegexPattern
from .patterns import Or
from .utils import reduce_regex_list, find_merge_ways
from regexfactory.pattern import RegexPattern, ValidPatternType


class CharRegexPattern(RegexPattern):
    """
    Char-level Regex Pattern
    """
    def __or__(self, a) -> 'CharRegexPattern':
        if isinstance(a, CharRegexPattern):
            union_examples = set.union(self.examples, a.examples)
            # check if the examples match those of the special characters
            if sp_char_regex:=SpecialCharRegexPattern.match_special_char_regex(union_examples):
                return sp_char_regex
            ascii_list = sorted([ord(x) for x in union_examples])
            # seperate examples into consecutive groups
            ascii_groups = CharRegexPattern._group_consecutive(ascii_list)
            simple_group = [x[0] for x in ascii_groups if len(x) == 1]
            for x in ascii_groups:
                if len(x) == 2:
                   simple_group.extend(x)
            other_groups = [x for x in ascii_groups if len(x) >= 3]
            # check if any of the groups have size > 3 and match them to Range(s)
            # for the others match them to a Set
            the_ranges = [Range(chr(group[0]), chr(group[-1])) for group in other_groups]
            if simple_group:
                the_set = Set(*[chr(ch) for ch in sorted(simple_group)])
                regex_groups = the_ranges + [the_set]
            else:
                regex_groups = the_ranges
            # check if any of the combination of groups match those special characters
            mapping = find_merge_ways(regex_groups, example_inference_callable=SpecialCharRegexPattern.match_special_char_regex)
            regex_groups = reduce_regex_list(regex_groups, mapping=mapping)
            if len(regex_groups) > 1:
                return Or(*regex_groups)
            elif len(regex_groups) == 1:
                return regex_groups[0]
            else:
                return Set(*sorted(list(union_examples)))
        elif isinstance(a, Or):
            if all(map(lambda x: isinstance(x, CharRegexPattern), a._patterns)):
                union_examples = reduce(lambda x,y: x|y, map(lambda m: m.examples, a._patterns))
                return self | Set(*list(union_examples))
            else:
                return Or(self, a)
        else:
            return Or(self, a)

    @staticmethod
    def _group_consecutive(ascii_list):
        groups = []
        for i, ascii in enumerate(ascii_list):
            if i == 0:
                group = [ascii]
                groups.append(group)
            else:
                if ascii_list[i-1] + 1 == ascii:
                    group.append(ascii)
                else:
                    group = [ascii]
                    groups.append(group)
                    
        return groups

class SpecialCharRegexPattern(CharRegexPattern):
    @staticmethod
    def match_special_char_regex(examples) -> Optional['SpecialCharRegexPattern']:
        if isinstance(examples, list):
            examples = set(examples)
        for special_char in [ANY, DIGIT, WORD, WHITESPACE]:
            if examples == special_char.examples:
                return special_char
#: (Dot.) In the default mode, this matches any character except a newline. If the :data:`re.DOTALL` flag has been specified, this matches any character including a newline.
ANY = SpecialCharRegexPattern(r".")

#: (Caret.) Matches the start of the string, and in  :data:`re.MULTILINE` mode also matches immediately after each newline.
ANCHOR_START = SpecialCharRegexPattern(r"^")

#: Matches the end of the string or just before the newline at the end of the string, and in :data:`re.MULTILINE` mode also matches before a newline. foo matches both :code:`foo` and :code:`foobar`, while the regular expression :code:`foo$` matches only :code:`foo`. More interestingly, searching for :code:`foo.$` in :code:`foo1\nfoo2\n` matches :code:`foo2` normally, but :code:`foo1` in  :data:`re.MULTILINE` mode; searching for a single $ in :code:`foo\n` will find two (empty) matches: one just before the newline, and one at the end of the string.
ANCHOR_END = SpecialCharRegexPattern(r"$")

#: Matches Unicode whitespace characters (which includes :code:`[ \t\n\r\f\v]`, and also many other characters, for example the non-breaking spaces mandated by typography rules in many languages). If the :data:`re.ASCII` flag is used, only :code:`[ \t\n\r\f\v]` is matched.
WHITESPACE = SpecialCharRegexPattern(r"\s")

#: Matches any character which is not a whitespace character. This is the opposite of \s. If the :data:`re.ASCII` flag is used this becomes the equivalent of :code:`[^ \t\n\r\f\v]`.
NOTWHITESPACE = SpecialCharRegexPattern(r"\S")

#: Matches Unicode word characters; this includes most characters that can be part of a word in any language, as well as numbers and the underscore. If the :data:`re.ASCII` flag is used, only :code:`[a-zA-Z0-9_]` is matched.
WORD = SpecialCharRegexPattern(r"\w")

#: Matches any character which is not a word character. This is the opposite of \w. If the :data:`re.ASCII` flag is used this becomes the equivalent of :code:`[^a-zA-Z0-9_]`. If the  :data:`re.LOCALE` flag is used, matches characters which are neither alphanumeric in the current locale nor the underscore.
NOTWORD = SpecialCharRegexPattern(r"\W")

#: Matches any Unicode decimal digit (that is, any character in Unicode character category [Nd]). This includes :code:`[0-9]`, and also many other digit characters. If the :data:`re.ASCII` flag is used only :code:`[0-9]` is matched.
DIGIT = SpecialCharRegexPattern(r"\d")

#: Matches any character which is not a decimal digit. This is the opposite of \d. If the :data:`re.ASCII` flag is used this becomes the equivalent of :code:`[^0-9]`.
NOTDIGIT = SpecialCharRegexPattern(r"\D")



class Range(CharRegexPattern):
    """
    For matching characters between two character indices
    (using the Unicode numbers of the input characters.)
    You can find use :func:`chr` and :func:`ord`
    to translate characters their Unicode numbers and back again.
    For example, :code:`chr(97)` returns the string :code:`'a'`,
    while :code:`chr(8364)` returns the string :code:`'€'`
    Thus, matching characters between :code:`'a'` and :code:`'z'`
    is really checking whether a characters unicode number
    is between :code:`ord('a')` and :code:`ord('z')`

    .. exec_code::

        from regexfactory import Range, Or

        patt = Or("Bob", Range("a", "z"))

        print(patt.findall("my job is working for Bob"))

    """

    def __init__(self, start: str, stop: str) -> None:
        self.start = start
        self.stop = stop
        regex = f"[{start}-{stop}]"
        super().__init__(regex)


class Set(CharRegexPattern):
    """
    For matching a single character from a list of characters.
    Keep in mind special characters like :code:`+` and :code:`.`
    lose their meanings inside a set/list,
    so need to escape them here to use them.

    In practice, :code:`Set("a", ".", "z")`
    functions the same as :code:`Or("a", ".", "z")`
    The difference being that :class:`Or` accepts :class:`RegexPattern` 's
    and :class:`Set` accepts characters only.
    Special characters do **NOT** lose their special meaings inside an :class:`Or` though.
    The other big difference is performance,
    :class:`Or` is a lot slower than :class:`Set`.

    .. exec_code::

        import time
        from regexfactory import Or, Set

        start_set = time.time()
        print(patt := Set(*"a.z").compile())
        print("Set took", time.time() - start_set, "seconds to compile")
        print("And the resulting match is", patt.match("b"))

        print()

        start_or = time.time()
        print(patt := Or(*"a.z").compile())
        print("Or took", time.time() - start_or, "seconds to compile")
        print("And the resulting match is", patt.match("b"))

    """

    def __init__(self, *patterns: ValidPatternType) -> None:
        regex = ""
        for pattern in patterns:
            if isinstance(pattern, Range):
                regex += f"{pattern.start}-{pattern.stop}"
            else:
                regex += self.get_regex(pattern)
        super().__init__(f"[{regex}]")
        self._patterns = patterns

class NotSet(CharRegexPattern):
    """
    For matching a character that is **NOT** in a list of characters.
    Keep in mind special characters lose their special meanings inside :class:`NotSet`'s as well.

    .. exec_code::

        from regexfactory import NotSet, Set

        not_abc = NotSet(*"abc")

        is_abc = Set(*"abc")

        print(not_abc.match("x"))
        print(is_abc.match("x"))

    """

    def __init__(self, *patterns: ValidPatternType) -> None:
        regex = ""
        for pattern in patterns:
            if isinstance(pattern, Range):
                regex += f"{pattern.start}-{pattern.stop}"
            else:
                regex += self.get_regex(pattern)
        super().__init__(f"[^{regex}]")
        self._patterns = patterns