class Atomic:
    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Atomic) and self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def apply_right(self, sequent):
        return None

    def apply_left(self, sequent):
        return None