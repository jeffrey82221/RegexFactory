# RegexFactory

Dynamically construct python regex patterns.

## Examples

### Matching Initials

Say you want a regex pattern to match the initials of someones name.

```python
import re
from regexfactory import Amount, Range


pattern = Amount(Range("A", "Z"), 2, 3)

matches = pattern.findall(
    "My initials are BDP. Valorie's are VO"
)

print(matches)
```

```bash
['BDP', 'VO']
```

### Matching Hex Strings

Or how matching both uppercase and lowercase hex strings in a sentence.

```python
import re
from regexfactory import *

pattern = Optional("#") + Or(
    Amount(
        Set(
            Range("0", "9"),
            Range("a", "f")
        ),
        6
    ),
    Amount(
        Set(
            Range("0", "9"),
            Range("A", "F")
        ),
        6
    ),

)

sentence = """
My favorite color is #000000. I also like 5fb8a0. My second favorite color is #FF21FF.
"""

matches = pattern.findall(sentence)
print(matches)
```

```bash
['#000000', '5fb8a0', '#FF21FF']
```

### Matching URLs

Or what if you want to match urls in html content?

```python
from regexfactory import *


protocol = Amount(Range("a", "z"), 1, or_more=True)
host = Amount(Set(WORD, DIGIT, '.'), 1, or_more=True)
port = Optional(IfBehind(":") + Multi(DIGIT))
path = Multi(
    RegexPattern('/') + Multi(
        NotSet('/', '#', '?', '&', WHITESPACE),
        match_zero=True
    ),
    match_zero=True
)
patt = protocol + RegexPattern("://") + host + port + path



sentence = "This is a cool url, https://github.com/GrandMoff100/RegexFactory/ "
print(patt)

print(patt.search(sentence))
```

```bash
[a-z]{1,}://[\w\d.]{1,}(?:\d{1,})?(/([^/#?&\s]{0,})){0,}
<re.Match object; span=(15, 51), match='https://github.com/GrandMoff100/RegexFactory/'>
```

## The Pitch

This library is really good at allowing you to intuitively understand how to construct a regex expression.
It helps you identify what exactly your regular expression is, and can help you debug it.
This is library is also very helpful for generating regex expressions on the fly if you find uses for it.
You can also extend this library by subclassing `RegexPattern` and add your own support for different regex flavors.
Like generating regex expresison with Perl5 extensions.

There you have it. This library is intuitive, extensible, modular, and dynamic.
Why not use it?

## Classes:

### Char-level Regex:

#### A: Special Chars 

ANY -> ascii 32~122 
(ANCHOR_START)
(ANCHOR_END)
WHITESPACE -> ascii 9~13 & 32 [ \t\n\r\f\v]
NOTWHITESPACE 
WORD -> ascii 48~255 [a-zA-Z0-9_]
NOTWORD
DIGIT -> ascii 48~57 [0-9]
NOTDIGIT

#### B: Complex Chars

Range
Set
NotSet

### Algorithm Design 

1. Given two char-level regex `x` and `y`, and identify their corresponding matching char set `Sx` and `Sy`.

```python
x = Range('a', 'w')
y = Set(*['x', 'y', 'z'])
...
Sx => {'a', 'b', 'c', ..., 'w'}
Sy => {'x', 'y', 'z'}
```
2. Do __and__ or __or__ operator between `Sx` and `Sy` and obtain the resulting set `Sz`.

```python
# if op == 'and':
    # Sz = Sx & Sy
# if op == 'or':
Sz = Sx | Sy
...
Sz => {'a', 'b', ..., 'z'}
```

3. Sort the char in `Sz` according to their ascii code (or unicode) order. 

```python
Sz = ['a', ..., 'z']
```

4. Group the consecutive chars. 

```
Sz -> G1, G2, ... 
G1 = ['a', ..., 'z']
G2 -> not G2 in this example.
```
5. Make each group a `Range` class for those group with more than 2 elements. 

G1 -> Range('a', 'z')

6.1. Convert Ranges to matching special char 

[0-9] -> [\d]

6.2. Combine each non-consecutive groups using `Set`. 

6.3. Convert Set to NotSet if its invert has shorter length.

# Complex Classes

Amount
Multi
Optional
Or

### Algorithm Design for same-class operation 

#### Amount 

```
A1 = Amount(pattern1, i1, j1, or_more=b1) 
A2 = Amount(pattern2, i2, j2, or_more=b2)

if pattern1 != pattern2:
    return Or(A1, A2)
elif j1!=None and j2!=None:
    if i1~j1, i2~j2 intersect:
        i3, j3 = join/intersec(i1~j1, i2~j2)
        return Amount(pattern1, i3, j3)
    else:
        return Or(A1, A2) / ''
elif j1!=None and b2=True:
    return Amount(pattern1, j1, or_more=True)
```


#### Multi 

#### Optional 

#### Or

# Advance Classes:

Extension
NamedGroup
NamedReference
NumberedReference
Comment
IfAhead
IfNotAhead
IfBehind
IfNotBehind
Group
IfGroup