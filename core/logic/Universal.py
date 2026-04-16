class Universal:
    def __init__(self, var, formula):
        self.var = var
        self.formula = formula

    def __str__(self):
        return f"∀{self.var}.{self.formula}"

    def __eq__(self, other):
        return isinstance(other, Universal) and self.var == other.var and self.formula == other.formula

    def __hash__(self):
        return hash((self.var, self.formula))

    def apply_right(self, sequent):
        antecedent, succedent = sequent
        if isinstance(succedent, Universal):
            # Approximate ∀R: Γ ⇒ ∀x.A from Γ ⇒ A
            return ([(antecedent, self.formula)], 'single')
        return None

    def apply_left(self, sequent):
        antecedent, succedent = sequent
        if self in antecedent:
            idx = antecedent.index(self)
            base = antecedent[:idx] + antecedent[idx+1:]
            # Approximate ∀L: Γ, ∀x.A ⇒ C from Γ, A ⇒ C
            new_ant = base + (self.formula,)
            return ([(new_ant, succedent)], 'single')
        return None
