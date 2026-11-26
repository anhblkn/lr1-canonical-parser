"""
main.py - builds the canonical LR(1) collection, prints/saves everything the
report needs, and parses the required input (plus the nested-for extension).

usage:
    python src/main.py                       # required input + nested input
    python src/main.py --input "stmt eof"    # also parse your own token list
"""

import argparse
import shutil
import subprocess
from pathlib import Path

from lr1 import (EOF, NONTERMINALS, TERMINALS, PRODUCTIONS, FIRST, Item, closure,
                 build_all, item_text, prod_text, sort_items, action_text,
                 first_of_string, next_symbol)
from lr_driver import parse, rows_to_markdown, ParseError
from ast_nodes import tree_lines
from automaton import to_dot, ast_to_dot

REQUIRED = "for ( init ; id ; step ) stmt eof"
NESTED = "for ( init ; id ; step ) for ( init ; id ; step ) stmt eof"


def write(path, text):
    Path(path).write_text(text + "\n", encoding="utf-8")


def cc0_report():
    log = []
    cc0 = closure([Item(0, 0, EOF)], log)
    out = ["Seed: %s" % item_text(Item(0, 0, EOF)), "",
           "Closure additions (triggering item -> added item, lookahead reason):"]
    for trig, new, beta, las in log:
        b = " ".join(beta) if beta else "ε"
        out.append("  %s -> %s   beta = %s, a = %s, FIRST(beta a) = {%s}"
                   % (item_text(trig), item_text(new), b, trig.la, ", ".join(sorted(las))))
    out += ["", "Complete CC0:"] + ["  " + item_text(i) for i in sort_items(cc0)]
    return "\n".join(out)


def item_sets_report(states, transitions):
    origin = {}
    for (i, X), j in transitions.items():
        origin.setdefault(j, (i, X))
    out = []
    for n, st in enumerate(states):
        head = "CC%d" % n if n not in origin else "CC%d = goto(CC%d, %s)" % ((n,) + origin[n])
        out.append(head)
        out += ["    " + item_text(i) for i in sort_items(st)]
        out.append("")
    return "\n".join(out)


def goto_record_report(goto_log):
    out = ["| From | Symbol | To | New or reused |", "|---|---|---|---|"]
    for i, X, j, status in goto_log:
        out.append("| CC%d | %s | CC%d | %s |" % (i, X, j, status))
    return "\n".join(out)


def tables_report(states, action, goto_table):
    cols = TERMINALS + [n for n in NONTERMINALS if n != "Goal"]
    out = ["| State | " + " | ".join(cols) + " |", "|" + "---|" * (len(cols) + 1)]
    for i in range(len(states)):
        cells = []
        for c in cols:
            if c in TERMINALS:
                cells.append(action_text(action.get((i, c))))
            else:
                cells.append(str(goto_table[(i, c)]) if (i, c) in goto_table else "")
        out.append("| %d | " % i + " | ".join(cells) + " |")
    return "\n".join(out)


def lookahead_report():
    out = ["| Expanded B | Suffix beta | Inherited a | FIRST(beta a) |", "|---|---|---|---|"]
    # the four closure situations of the header / body: item [S -> for ( . I ; C ; U ) S, eof] etc.
    rhs = PRODUCTIONS[1][1]
    for name, pos in (("I", 2), ("C", 4), ("U", 6), ("S (body)", 8)):
        beta = rhs[pos + 1:]
        out.append("| %s | %s | eof | {%s} |" % (name, " ".join(beta) if beta else "ε",
                                                 ", ".join(sorted(first_of_string(beta, EOF)))))
    return "\n".join(out)


def ast_report(snapshots, root):
    out = []
    for k, s in enumerate(snapshots, 1):
        out.append("Reduction %d  step %d  rule %s" % (k, s["step"], s["rule"]))
        out.append("  value: %s" % s["value"])
        out.append("  reused nodes: %s" % (", ".join(s["reused"]) or "none"))
        out.append("  new node: %s" % s["new"])
        out.append("  available subtrees:")
        for tree in s["forest"]:
            out += ["    " + line for line in tree_lines(tree)]
        out.append("")
    out.append("Root: %s" % root.label)
    return "\n".join(out)


def render_png(dot_text, path):
    """draw a DOT string to a png (needs Graphviz, silently skipped if missing)"""
    if shutil.which("dot"):
        subprocess.run(["dot", "-Tpng", "-Gdpi=200", "-o", str(path)], input=dot_text,
                       text=True, check=True)


def run_input(name, text, action, goto_table, outdir):
    rows, snaps, root, factory = parse(text.split(), action, goto_table)
    write(outdir / ("trace_%s.md" % name),
          "Input: `%s`\n\n%s\n\nFinal outcome: accept, root value: %s"
          % (text, rows_to_markdown(rows), root.definition()))
    write(outdir / ("ast_%s.txt" % name),
          ast_report(snaps, root) + "\nReductions: %d   AST nodes: %d\n\n%s"
          % (len(snaps), len(factory.created), "\n".join(tree_lines(root))))
    figs = outdir / "figures"
    figs.mkdir(exist_ok=True)
    for k, s in enumerate(snaps, 1):
        render_png(ast_to_dot(s["forest"], s["new"]), figs / ("ast_%s_reduction%d.png" % (name, k)))
    render_png(ast_to_dot([root], root.label), figs / ("ast_%s_final.png" % name))
    print("\n== trace: %s ==" % name)
    print(rows_to_markdown(rows))
    print("root:", root.definition(), "| nodes:", len(factory.created))
    return rows, root


def main():
    ap = argparse.ArgumentParser(description="canonical LR(1) parser for the coursework grammar")
    ap.add_argument("--input", help="extra token list to parse, must end with eof")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "output"))
    args = ap.parse_args()
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    states, transitions, goto_log, action, goto_table = build_all()

    write(outdir / "cc0_closure.txt", cc0_report())
    write(outdir / "item_sets.txt", item_sets_report(states, transitions))
    write(outdir / "goto_record.md", goto_record_report(goto_log))
    write(outdir / "action_goto_table.md", tables_report(states, action, goto_table))
    write(outdir / "closure_lookaheads.md", lookahead_report())
    write(outdir / "automaton.dot", to_dot(states, transitions, action))
    if shutil.which("dot"):
        subprocess.run(["dot", "-Tpng", "-Gdpi=150", str(outdir / "automaton.dot"), "-o",
                        str(outdir / "automaton.png")], check=True)
        (outdir / "figures").mkdir(exist_ok=True)
        render_png(to_dot(states, transitions, action, compact=True),
                   outdir / "figures" / "automaton_compact.png")

    print("states: %d   edges: %d" % (len(states), len(transitions)))
    print(tables_report(states, action, goto_table))

    run_input("required", REQUIRED, action, goto_table, outdir)
    run_input("nested", NESTED, action, goto_table, outdir)
    if args.input:
        try:
            run_input("custom", args.input, action, goto_table, outdir)
        except ParseError as e:
            print("\nparse error:", e)


if __name__ == "__main__":
    main()
