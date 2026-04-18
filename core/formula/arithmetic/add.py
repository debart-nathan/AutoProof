from ...interfaces.formula import Formula

class Add(Formula):
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def apply_right(self, sequent):
        return None

    def apply_left(self, sequent):
        return None

    def substitute(self, var, term):
        return Add(
            self.left.substitute(var, term),
            self.right.substitute(var, term)
        )

    def rewrite_once(self):
        from .zero import Zero
        from .succ import Succ

        if isinstance(self.left, Zero):
            return self.right, "add-left-zero"

        if isinstance(self.left, Succ):
            return Succ(Add(self.left.inner, self.right)), "add-left-succ"

        new_left, rule = self.left.rewrite_once()
        if new_left is not None:
            return Add(new_left, self.right), rule

        new_right, rule = self.right.rewrite_once()
        if new_right is not None:
            return Add(self.left, new_right), rule

        return None, None

    def simplify(self):
        term = self
        while True:
            new_term, rule = term.rewrite_once()
            if new_term is None:
                return term
            term = new_term

    def __str__(self):
        return f"({self.left} + {self.right})"

    def __eq__(self, other):
        return (
            isinstance(other, Add)
            and self.left == other.left
            and self.right == other.right
        )

    def __hash__(self):
        return hash(("add", self.left, self.right))
