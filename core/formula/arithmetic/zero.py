from ...interfaces.formula import Formula

class Zero(Formula):
    def apply_right(self, sequent):
        return None

    def apply_left(self, sequent):
        return None

    def substitute(self, var, term):
        return self

    def rewrite_once(self):
        return None, None

    def __str__(self):
        return "0"

    def __eq__(self, other):
        return isinstance(other, Zero)

    def __hash__(self):
        return hash("zero")
