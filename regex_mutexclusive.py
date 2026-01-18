# automata-lib

from automata.fa.nfa import NFA

# Example regexes (must be regular)
r1 = "(ab)*"
r2 = "a+b+"

nfa1 = NFA.from_regex(r1)
nfa2 = NFA.from_regex(r2)

# Intersection
intersection = nfa1.intersection(nfa2)

# Check emptiness
mutually_exclusive = intersection.is_empty()

print(mutually_exclusive)

import re

NON_REGULAR = re.compile(
    r"""
    \(\?=|\(\?!|\(\?<=|\(\?<!|   # lookarounds
    \\[1-9]|                     # backreferences
    \(\?\(|                       # conditional
    \\b|\\B
    """,
    re.VERBOSE,
)

def assert_regular(regex):
    if NON_REGULAR.search(regex):
        raise ValueError("Regex is not regular and cannot be converted")
