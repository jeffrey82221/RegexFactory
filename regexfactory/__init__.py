"""
API Reference
##############

The regexfactory module documentation!

.. automodule:: regexfactory.pattern

.. automodule:: regexfactory.patterns

.. automodule:: regexfactory.chars

"""

from .chars import (
    ANCHOR_END,
    ANCHOR_START,
    ANY,
    DIGIT,
    NOTDIGIT,
    NOTWHITESPACE,
    NOTWORD,
    WHITESPACE,
    WORD,
)
from .pattern import ESCAPED_CHARACTERS, RegexPattern, ValidPatternType, escape, join
from .extension import (
    Comment,
    Extension,
    Group,
    IfAhead,
    IfBehind,
    IfGroup,
    IfNotAhead,
    IfNotBehind,
    NamedGroup,
    NamedReference,
    NumberedReference
)
from .patterns import (
    Amount,
    Multi,
    Optional,
    Or
)
from .chars import (
    Range,
    Set,
    NotSet
)

__version__ = "1.0.0"
