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
