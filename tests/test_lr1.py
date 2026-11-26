"""unit tests - run with:  python -m unittest discover -s tests -v"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lr1 import build_all, Item, closure, item_text, sort_items, action_text, EOF  # noqa: E402
from lr_driver import parse, ParseError  # noqa: E402

REQUIRED = "for ( init ; id ; step ) stmt eof".split()
NESTED = "for ( init ; id ; step ) for ( init ; id ; step ) stmt eof".split()


class CanonicalCollectionTests(unittest.TestCase):
    def setUp(self):
        (self.states, self.transitions, self.goto_log,
         self.action, self.goto_table) = build_all()

    def test_cc0_has_three_items(self):
        cc0 = [item_text(i) for i in sort_items(self.states[0])]
        self.assertEqual(cc0, ["[Goal → • S, eof]",
                               "[S → • for ( I ; C ; U ) S, eof]",
                               "[S → • stmt, eof]"])

    def test_counts(self):
        self.assertEqual(len(self.states), 15)
        self.assertEqual(len(self.transitions), 16)

    def test_reused_states(self):
        reused = [(i, x, j) for i, x, j, s in self.goto_log if s == "reused"]
        self.assertEqual(reused, [(13, "for", 2), (13, "stmt", 3)])

    def test_header_lookaheads(self):
        self.assertEqual([item_text(i) for i in self.states[4] if i.prod == 3], ["[I → • init, ;]"])
        self.assertEqual([item_text(i) for i in self.states[7] if i.prod == 4], ["[C → • id, ;]"])
        self.assertEqual([item_text(i) for i in self.states[10] if i.prod == 5], ["[U → • step, )]"])

    def test_body_state_closure(self):
        self.assertEqual(len(self.states[13]), 3)
        self.assertTrue(all(i.la == EOF for i in self.states[13]))

    def test_action_table_entries(self):
        expected = {(0, "for"): "s2", (0, "stmt"): "s3", (1, EOF): "acc", (2, "("): "s4",
                    (3, EOF): "r2", (4, "init"): "s6", (5, ";"): "s7", (6, ";"): "r3",
                    (7, "id"): "s9", (8, ";"): "s10", (9, ";"): "r4", (10, "step"): "s12",
                    (11, ")"): "s13", (12, ")"): "r5", (13, "for"): "s2", (13, "stmt"): "s3",
                    (14, EOF): "r1"}
        got = {k: action_text(v) for k, v in self.action.items()}
        self.assertEqual(got, expected)

    def test_goto_table_entries(self):
        self.assertEqual(self.goto_table, {(0, "S"): 1, (4, "I"): 5, (7, "C"): 8,
                                           (10, "U"): 11, (13, "S"): 14})


class ParserTests(unittest.TestCase):
    def setUp(self):
        *_, self.action, self.goto_table = build_all()

    def test_required_input(self):
        rows, snaps, root, factory = parse(REQUIRED, self.action, self.goto_table)
        self.assertEqual(len(rows), 21)                      # steps 0..20
        self.assertEqual(len(snaps), 5)                      # five reductions
        self.assertEqual(root.definition(), "F1 = For(I1, C1, U1, B1)")
        self.assertEqual(len(factory.created), 5)
        self.assertEqual(rows[-1][1].split()[0], "Accept")
        self.assertEqual([c.kind for c in root.children],
                         ["Init", "Identifier", "Update", "BasicStmt"])

    def test_only_shifts_consume_input(self):
        rows, *_ = parse(REQUIRED, self.action, self.goto_table)
        lengths = [len(r[3].split()) for r in rows]
        for prev, cur, row in zip(lengths, lengths[1:], rows[1:]):
            if not row[1].startswith("Shift"):
                self.assertEqual(prev, cur)

    def test_nested_input(self):
        rows, snaps, root, factory = parse(NESTED, self.action, self.goto_table)
        self.assertEqual(root.definition(), "F2 = For(I1, C1, U1, F1)")
        inner = root.children[3]
        self.assertEqual(inner.definition(), "F1 = For(I2, C2, U2, B1)")
        self.assertEqual(len(factory.created), 9)

    def test_syntax_error(self):
        with self.assertRaises(ParseError):
            parse("for ( init ; id ) stmt eof".split(), self.action, self.goto_table)
        with self.assertRaises(ParseError):
            parse("for ( init ; id ; step ) eof".split(), self.action, self.goto_table)


if __name__ == "__main__":
    unittest.main()
