from .Checker import Checker

class Prover:
    def __init__(self, max_depth: int = 100):
        self.max_depth = max_depth
        self.memo = {}

    def prove(self, sequent, depth: int = 0) -> str:
        if depth > self.max_depth:
            return "unknown"

        antecedent, succedent = sequent

        # Canonical antecedent for both memoization AND rule application
        sorted_antecedent = tuple(sorted(antecedent, key=str))
        canonical_sequent = (sorted_antecedent, succedent)

        # Memo lookup
        if canonical_sequent in self.memo:
            return self.memo[canonical_sequent]

        # Axiom rule
        if succedent in sorted_antecedent:
            self.memo[canonical_sequent] = "proven"
            return "proven"

        # Right rules
        result_right = succedent.apply_right(canonical_sequent)
        if result_right is not None:
            premises, conn_type = result_right
            if self.handle_premises(premises, conn_type, depth):
                self.memo[canonical_sequent] = "proven"
                return "proven"

        # Left rules (use canonical antecedent)
        for formula in sorted_antecedent:
            result_left = formula.apply_left(canonical_sequent)
            if result_left is not None:
                premises, conn_type = result_left
                if self.handle_premises(premises, conn_type, depth):
                    self.memo[canonical_sequent] = "proven"
                    return "proven"

        self.memo[canonical_sequent] = "unknown"
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
