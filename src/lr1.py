"""
lr1.py - canonical LR(1) construction for the CSC 4343 coursework grammar.

Production numbering follows the answer-sheet template:
    0: Goal -> S
    1: S -> for ( I ; C ; U ) S
    2: S -> stmt
    3: I -> init
    4: C -> id
    5: U -> step

Everything here is built from the definitions in the lectures:
closure, goto, the canonical collection CC and then ACTION / GOTO.
"""

from collections import namedtuple

EOF = "eof"

PRODUCTIONS = [
    ("Goal", ("S",)),
    ("S", ("for", "(", "I", ";", "C", ";", "U", ")", "S")),
    ("S", ("stmt",)),
    ("I", ("init",)),
    ("C", ("id",)),
    ("U", ("step",)),
]

NONTERMINALS = ["Goal", "S", "I", "C", "U"]
# same column order as the ACTION table in the answer sheet
TERMINALS = ["for", "(", "init", ";", "id", "step", ")", "stmt", EOF]

# An LR(1) item is [A -> alpha . beta, a]:  prod = index into PRODUCTIONS,
# dot = position of the dot in the right hand side, la = lookahead terminal.
Item = namedtuple("Item", ["prod", "dot", "la"])


class ConflictError(Exception):
    """Raised if two different actions want the same ACTION cell."""


# ---------------------------------------------------------------- FIRST sets
def _first_of_symbol(sym, first):
    return {sym} if sym in TERMINALS else first[sym]


def compute_first():
    """FIRST sets for the nonterminals (no nonterminal is nullable here)."""
    first = {nt: set() for nt in NONTERMINALS}
    changed = True
    while changed:
        changed = False
        for lhs, rhs in PRODUCTIONS:
            new = _first_of_symbol(rhs[0], first)
            if not new <= first[lhs]:
                first[lhs] |= new
                changed = True
    return first


FIRST = compute_first()


def first_of_string(beta, a):
    """FIRST(beta a).  Since nothing is nullable, it is FIRST(beta[0]) when
    beta is not empty, otherwise just {a}."""
    if beta:
        return set(_first_of_symbol(beta[0], FIRST))
    return {a}


# ------------------------------------------------------------ item helpers
def item_text(item):
    lhs, rhs = PRODUCTIONS[item.prod]
    left = " ".join(rhs[:item.dot])
    right = " ".join(rhs[item.dot:])
    body = " ".join(x for x in (left, "•", right) if x)
    return "[%s → %s, %s]" % (lhs, body, item.la)


def prod_text(p):
    lhs, rhs = PRODUCTIONS[p]
    return "%s → %s" % (lhs, " ".join(rhs))


def sort_items(items):
    # kernel items first (dot moved, or the Goal seed), closure items after them
    return sorted(items, key=lambda it: (it.dot == 0 and it.prod != 0,
                                         it.prod, it.dot, TERMINALS.index(it.la)))


def next_symbol(item):
    rhs = PRODUCTIONS[item.prod][1]
    return rhs[item.dot] if item.dot < len(rhs) else None


# ----------------------------------------------------------- closure / goto
def closure(kernel, log=None):
    """closure of a set of items.  If log is a list, every item that gets added
    is appended as (triggering item, added item, beta, FIRST(beta a))."""
    items = list(kernel)
    seen = set(items)
    i = 0
    while i < len(items):
        it = items[i]
        i += 1
        B = next_symbol(it)
        if B is None or B not in NONTERMINALS:
            continue
        beta = PRODUCTIONS[it.prod][1][it.dot + 1:]
        lookaheads = first_of_string(beta, it.la)
        for p, (lhs, _) in enumerate(PRODUCTIONS):
            if lhs != B:
                continue
            for b in sorted(lookaheads, key=TERMINALS.index):
                new = Item(p, 0, b)
                if new not in seen:
                    seen.add(new)
                    items.append(new)
                    if log is not None:
                        log.append((it, new, beta, lookaheads))
    return frozenset(items)


def goto(state, X):
    """move the dot over X in every item that allows it, then take closure"""
    kernel = [Item(it.prod, it.dot + 1, it.la) for it in state if next_symbol(it) == X]
    return closure(kernel)


def _symbol_order(symbols):
    # nonterminals first (in grammar order) then terminals (in table order)
    def key(s):
        if s in NONTERMINALS:
            return (0, NONTERMINALS.index(s))
        return (1, TERMINALS.index(s))
    return sorted(symbols, key=key)


# --------------------------------------------------- canonical collection
def build_collection():
    """Returns (states, transitions, goto_log).

    states       list of frozensets of items, states[i] is CCi
    transitions  dict {(i, X): j}
    goto_log     list of (i, X, j, 'new' | 'reused') in the order they were found
    """
    start = closure([Item(0, 0, EOF)])
    states = [start]
    index = {start: 0}
    transitions = {}
    goto_log = []
    i = 0
    while i < len(states):
        syms = {next_symbol(it) for it in states[i]} - {None}
        for X in _symbol_order(syms):
            target = goto(states[i], X)
            if target in index:
                status = "reused"
            else:
                index[target] = len(states)
                states.append(target)
                status = "new"
            transitions[(i, X)] = index[target]
            goto_log.append((i, X, index[target], status))
        i += 1
    return states, transitions, goto_log


# ------------------------------------------------------- ACTION and GOTO
def build_tables(states, transitions):
    action = {}
    goto_table = {}

    def put(key, value):
        if key in action and action[key] != value:
            raise ConflictError("conflict at %s: %s vs %s" % (key, action[key], value))
        action[key] = value

    for (i, X), j in transitions.items():
        if X in NONTERMINALS:
            goto_table[(i, X)] = j
        else:
            put((i, X), ("shift", j))
    for i, state in enumerate(states):
        for it in state:
            if next_symbol(it) is None:           # completed item
                if it.prod == 0 and it.la == EOF:
                    put((i, EOF), ("accept", None))
                else:
                    put((i, it.la), ("reduce", it.prod))
    return action, goto_table


def action_text(entry):
    if entry is None:
        return ""
    kind, n = entry
    if kind == "accept":
        return "acc"
    return ("s" if kind == "shift" else "r") + str(n)


def build_all():
    states, transitions, goto_log = build_collection()
    action, goto_table = build_tables(states, transitions)
    return states, transitions, goto_log, action, goto_table
