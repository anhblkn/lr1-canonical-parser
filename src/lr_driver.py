"""
lr_driver.py - table driven LR(1) driver.

The trace follows the answer-sheet convention: every row shows the
configuration AFTER the operation.  A reduction and its GOTO are two separate
rows and the new AST value is held as "pending" in between.  Only shifts
consume input.
"""

from lr1 import EOF, PRODUCTIONS, prod_text
from ast_nodes import NodeFactory, semantic_action


class ParseError(Exception):
    pass


def stack_text(stack):
    return " ".join("%s/CC%d" % (sym, st) for sym, st, _ in stack)


def parse(tokens, action, goto_table):
    """tokens must end with eof.  Returns (trace_rows, snapshots, root, factory).

    trace_rows  list of (step, operation, stack AFTER, remaining AFTER, pending/pushed)
    snapshots   one entry per reduction: dict with step, rule, value, reused, new
    """
    tokens = list(tokens)
    if not tokens or tokens[-1] != EOF:
        raise ParseError("input must end with eof")

    factory = NodeFactory()
    stack = [("$", 0, None)]                    # (symbol, state, semantic value)
    pos = 0
    rows = [(0, "Initialize", stack_text(stack), " ".join(tokens), "None")]
    snapshots = []

    def add(op, pending):
        rows.append((len(rows), op, stack_text(stack), " ".join(tokens[pos:]), pending))

    while True:
        state, la = stack[-1][1], tokens[pos]
        entry = action.get((state, la))
        if entry is None:
            raise ParseError("syntax error: no ACTION[CC%d, %s]" % (state, la))
        kind, n = entry

        if kind == "shift":
            stack.append((la, n, la))
            pos += 1                            # the only place input is consumed
            add("Shift %s, go to CC%d" % (la, n), "None")

        elif kind == "reduce":
            lhs, rhs = PRODUCTIONS[n]
            popped = stack[len(stack) - len(rhs):]
            vals = [v for _, _, v in popped]    # save RHS values BEFORE popping
            del stack[len(stack) - len(rhs):]
            value = semantic_action(factory, n, vals)
            exposed = stack[-1][1]
            add("Reduce r%d: %s (lookahead %s)" % (n, prod_text(n), la),
                "pending %s" % value.definition())
            reused = [v.label for v in vals if hasattr(v, "label")]
            snapshots.append({
                "step": rows[-1][0], "rule": "r%d: %s" % (n, prod_text(n)),
                "value": value.definition(), "reused": reused, "new": value.label,
                "forest": [v for _, _, v in stack if hasattr(v, "label")] + [value],
            })
            target = goto_table[(exposed, lhs)]
            stack.append((lhs, target, value))
            add("GOTO(CC%d, %s) = CC%d" % (exposed, lhs, target), "pushed %s" % value.label)

        else:                                    # accept
            root = stack[-1][2]
            add("Accept (ACTION[CC%d, %s] = acc)" % (state, la), "root %s" % root.definition())
            return rows, snapshots, root, factory


def rows_to_markdown(rows):
    out = ["| Step | Operation or lookup | Stack AFTER (bottom to top) | Remaining input AFTER | Pending or pushed AST value |",
           "|---|---|---|---|---|"]
    for r in rows:
        out.append("| %s | %s | `%s` | `%s` | %s |" % r)
    return "\n".join(out)
