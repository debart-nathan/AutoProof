from ...interfaces.formula import Formula

class Succ(Formula):
    def __init__(self, inner: Formula):
        self.inner = inner

    def apply_right(self, sequent):
        return None

    def apply_left(self, sequent):
        return None

    def substitute(self, var, term):
        return Succ(self.inner.substitute(var, term))

    def rewrite_once(self):
        new_inner, rule = self.inner.rewrite_once()
        if new_inner is not None:
            return Succ(new_inner), rule
        return None, None

    def __str__(self):
        return f"S({self.inner})"

    def __eq__(self, other):
        return isinstance(other, Succ) and self.inner == other.inner

    def __hash__(self):
        return hash(("succ", self.inner))
