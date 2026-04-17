"""Checker for logical rule applicability."""


class Checker:
    """Utility class for checking if rules can be applied to formulas."""

    @staticmethod
    def can_apply(sequent, formula) -> bool:
        """Check if a formula can apply any rule to the given sequent."""
        return formula.apply_right(sequent) is not None or formula.apply_left(sequent) is not None
