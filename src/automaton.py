"""
automaton.py - export the LR(1) automaton as a Graphviz DOT file.

One node per CCi, one labelled edge per GOTO.  The initial state gets an
incoming arrow, completed items are written inside the node together with the
reduce / accept action that comes from them.
"""

from lr1 import EOF, item_text, next_symbol, sort_items
from ast_nodes import FOR_ROLES


def completed_note(state_items, state_no, action):
    notes = []
    for it in sort_items(state_items):
        if next_symbol(it) is None:
            act = action[(state_no, it.la)]
            what = "ACCEPT" if act[0] == "accept" else "reduce r%d" % act[1]
            notes.append("%s\\n%s on %s" % (item_text(it), what, it.la))
    return notes


def to_dot(states, transitions, action, compact=False):
    """compact=True gives a narrower drawing that fits a table cell in Word"""
    lines = ["digraph LR1 {",
             "  rankdir=TB;",
             "  ranksep=%s; nodesep=%s;" % (("0.28", "0.3") if compact else ("0.5", "0.25")),
             '  node [shape=box, style=rounded, fontname="DejaVu Sans", fontsize=%d];' % (13 if compact else 12),
             '  edge [fontname="DejaVu Sans", fontsize=%d];' % (13 if compact else 12),
             '  start [shape=point, width=0.12];',
             "  start -> CC0;"]
    for i, items in enumerate(states):
        notes = completed_note(items, i, action)
        label = "CC%d" % i
        if notes:
            label += "\\n" + "\\n".join(notes)
        extra = ""
        if i == 0:
            extra = ', penwidth=2.2'               # initial state
        if action.get((i, EOF)) == ("accept", None):
            extra = ', peripheries=2, penwidth=2.2'  # accepting state
        lines.append('  CC%d [label="%s"%s];' % (i, label, extra))
    for (i, X), j in sorted(transitions.items()):
        lines.append('  CC%d -> CC%d [label=" %s "];' % (i, j, X.replace('"', '\\"')))
    lines.append("}")
    return "\n".join(lines)


def ast_to_dot(forest, new_label=None):
    """Draw the AST values that exist after a reduction.  `forest` is the list of
    root nodes (values on the stack), the node created by this reduction
    (new_label) gets a grey fill and a thick border; children keep their order."""
    lines = ["digraph AST {",
             "  graph [ordering=out, ranksep=0.35, nodesep=0.25];",
             '  node [shape=box, style="rounded,filled", fillcolor=white, fontname="DejaVu Sans", fontsize=13];',
             '  edge [fontname="DejaVu Sans", fontsize=11];']
    seen = set()

    def emit(node):
        if node.label in seen:
            return
        seen.add(node.label)
        text = node.kind if node.children else node.expr()
        extra = ', fillcolor="#dcdcdc", penwidth=2.2' if node.label == new_label else ""
        lines.append('  %s [label="%s\\n%s"%s];' % (node.label, node.label, text, extra))
        for role, child in zip(FOR_ROLES, node.children):
            emit(child)
            lines.append('  %s -> %s [label=" %s "];' % (node.label, child.label, role))

    for root in forest:
        emit(root)
    if len(forest) > 1:
        lines.append("  {rank=same; %s}" % "; ".join(r.label for r in forest))
    lines.append("}")
    return "\n".join(lines)
