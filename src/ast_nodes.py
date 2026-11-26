"""
ast_nodes.py - AST node classes and the semantic actions from Section 3.

Node ids are per node type and given in creation order, so the first Init node
is I1, the first For node is F1, the second For node would be F2, and so on.
"""

PREFIX = {"Init": "I", "Identifier": "C", "Update": "U", "BasicStmt": "B", "For": "F"}
FOR_ROLES = ["initialization", "condition", "update", "body"]


class Node:
    def __init__(self, kind, number, token=None, children=()):
        self.kind = kind
        self.number = number
        self.token = token            # only the leaf-like nodes keep their token
        self.children = list(children)

    @property
    def label(self):
        return "%s%d" % (PREFIX[self.kind], self.number)

    def expr(self):
        """e.g.  Init(init)   or   For(I1, C1, U1, B1)"""
        if self.kind == "For":
            return "For(%s)" % ", ".join(c.label for c in self.children)
        return "%s(%s)" % (self.kind, self.token)

    def definition(self):
        return "%s = %s" % (self.label, self.expr())


class NodeFactory:
    """hands out successive ids per node type, in creation order"""

    def __init__(self):
        self.counters = {k: 0 for k in PREFIX}
        self.created = []

    def make(self, kind, token=None, children=()):
        self.counters[kind] += 1
        node = Node(kind, self.counters[kind], token, children)
        self.created.append(node)
        return node


def semantic_action(factory, prod, vals):
    """vals = semantic values of the RHS symbols, left to right (saved BEFORE
    the stack entries are removed)."""
    if prod == 1:      # S -> for ( I ; C ; U ) S      F = For(I, C, U, B)
        return factory.make("For", children=[vals[2], vals[4], vals[6], vals[8]])
    if prod == 2:      # S -> stmt                     B = BasicStmt(stmt)
        return factory.make("BasicStmt", token=vals[0])
    if prod == 3:      # I -> init                     I = Init(init)
        return factory.make("Init", token=vals[0])
    if prod == 4:      # C -> id                       C = Identifier(id)
        return factory.make("Identifier", token=vals[0])
    if prod == 5:      # U -> step                     U = Update(step)
        return factory.make("Update", token=vals[0])
    raise ValueError("no semantic action for production %d" % prod)


def tree_lines(node, role=None, prefix="", last=True, top=True):
    """ASCII drawing of a subtree, showing the child roles of For nodes"""
    head = "%s %s" % (node.label, node.expr() if not node.children else node.kind)
    if role:
        head = "%s: %s" % (role, head)
    lines = [head] if top else [prefix + ("└── " if last else "├── ") + head]
    child_prefix = "" if top else prefix + ("    " if last else "│   ")
    for k, child in enumerate(node.children):
        lines += tree_lines(child, FOR_ROLES[k], child_prefix, k == len(node.children) - 1, False)
    return lines
