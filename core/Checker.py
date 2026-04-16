class Checker:
    @staticmethod
    def can_apply(sequent, formula) -> bool:
        return formula.apply_right(sequent) is not None or formula.apply_left(sequent) is not None