# Canonical LR(1) Parser – CSC 4343 Individual Coursework 1

This repository is the program that goes with my Word report for the
*Canonical LR1* coursework. I did the six stages by hand on the answer sheets
first, then wrote this small Python program to check my work: it builds the
canonical LR(1) collection, the ACTION/GOTO tables, runs the input trace and
builds the AST.

## Grammar

```
(0) Goal → S
(1) S → for ( I ; C ; U ) S
(2) S → stmt
(3) I → init
(4) C → id
(5) U → step
```

`init`, `id`, `step` and `stmt` are atomic tokens. Required input:

```
for ( init ; id ; step ) stmt eof
```

## Results in short

| Item | Result |
|---|---|
| Item sets (states) | 15 (CC0 … CC14) |
| GOTO edges | 16 (2 of them reuse an existing state: CC13 –for→ CC2 and CC13 –stmt→ CC3) |
| Conflicts | none, the grammar is LR(1) |
| Trace length | steps 0 … 20, ends with `acc` |
| Reductions | 5 (r3, r4, r5, r2, r1) |
| AST root | `F1 = For(I1, C1, U1, B1)` (4 ordered children: initialization, condition, update, body) |

## Folder structure

```
lr1-canonical-parser/
├── README.md
├── .gitignore
├── src/
│   ├── lr1.py          grammar, FIRST, closure, goto, canonical collection, ACTION/GOTO
│   ├── ast_nodes.py    AST node classes and the semantic actions from Section 3
│   ├── lr_driver.py    table-driven shift/reduce driver (trace AFTER each operation)
│   ├── automaton.py    Graphviz DOT export of the automaton
│   └── main.py         runs everything and writes the files in output/
├── tests/
│   └── test_lr1.py     unit tests (item sets, tables, trace, AST, nested input, errors)
└── output/             generated results (what I used to check the report)
    ├── cc0_closure.txt          Stage 1  – CC0 seed and closure additions
    ├── item_sets.txt            Stage 2  – all item sets CC0 … CC14
    ├── goto_record.md           Stage 2/3 – every GOTO transition, new or reused
    ├── automaton.dot / .png     Stage 3  – labelled automaton
    ├── action_goto_table.md     Stage 4  – ACTION and GOTO tables
    ├── closure_lookaheads.md    Stage 4  – FIRST(β a) for header and body
    ├── trace_required.md        Stage 5  – trace of the required input
    ├── ast_required.txt         Stage 6  – five reduction snapshots and final AST
    ├── trace_nested.md / ast_nested.txt   optional nested-for extension
    └── figures/                 PNGs used in the report (automaton + AST drawings)
```

## How to run

You only need Python 3.8 or newer (no extra packages). Graphviz (`dot`) is
optional and only used to draw `automaton.png`.

```bash
# from the repository root
python src/main.py

# parse your own token list (must end with eof)
python src/main.py --input "for ( init ; id ; step ) stmt eof"

# run the tests
python -m unittest discover -s tests -v
```

On some systems the command is `python3` instead of `python` (as I do work on MacBook)

## How it works (short version)

1. `closure` adds `[B → • γ, b]` for every `B → γ` and every `b ∈ FIRST(β a)`
   until nothing new appears. No nonterminal is nullable, so `FIRST(β a)` is
   just the first symbol of β, or `a` when β is empty.
2. `goto(I, X)` moves the dot over `X`, keeps the lookaheads and takes the
   closure. `build_collection` repeats this from CC0 until no new item set
   shows up and reuses a state when the full item set is equal.
3. `build_tables` puts `sN` for shifts, `rN` for completed items (using the
   item's own lookahead) and `acc` for `[Goal → S •, eof]`. It raises an error
   if two actions land in the same cell.
4. `lr_driver.parse` follows the tables. Each reduction saves the RHS values
   first, pops the stack, builds the AST node and holds it as *pending*, then a
   separate GOTO row pushes the LHS. Only shifts consume input, and `eof` is
   never shifted.
5. AST ids are given per node type in creation order (I1, C1, U1, B1, F1; with
   the nested input the inner `for` is F1 and the outer one is F2).

## Author

Anhelina Bilokon, student ID: 272666.
