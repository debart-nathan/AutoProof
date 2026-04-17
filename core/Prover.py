from .Checker import Checker
from .Sequent import Sequent

class Prover:
    def __init__(self, max_depth: int = 100):
        self.max_depth = max_depth
        self.memo = {}

    def prove(self, sequent, depth: int = 0) -> str:
        if depth > self.max_depth:
            return "unknown"

        # Convert tuple to Sequent if needed (backward compatibility)
        if isinstance(sequent, tuple):
            sequent = Sequent(sequent[0], sequent[1])

        # Memo lookup (Sequent has proper __hash__ and __eq__)
        if sequent in self.memo:
            return self.memo[sequent]

        # Axiom rule: if succedent is in context
        if sequent.contains_in_context(sequent.succedent):
            self.memo[sequent] = "proven"
            return "proven"

        # Right rules
        result_right = sequent.succedent.apply_right(sequent)
        if result_right is not None:
            premises, conn_type = result_right
            if self.handle_premises(premises, conn_type, depth):
                self.memo[sequent] = "proven"
                return "proven"

        # Left rules
        for formula in sequent.antecedent:
            result_left = formula.apply_left(sequent)
            if result_left is not None:
                premises, conn_type = result_left
                if self.handle_premises(premises, conn_type, depth):
                    self.memo[sequent] = "proven"
                    return "proven"

        self.memo[sequent] = "unknown"
        return "unknown"

    def handle_premises(self, premises, conn_type, depth):
        if conn_type == 'bottom-left':
            return True

        if conn_type == 'none':
            return False

        if conn_type == 'single':
            return self.prove(premises[0], depth + 1) == "proven"

        if conn_type == 'and':
            return all(self.prove(p, depth + 1) == "proven" for p in premises)

        if conn_type == 'or':
            return any(self.prove(p, depth + 1) == "proven" for p in premises)

        return False
