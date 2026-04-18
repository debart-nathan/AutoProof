from ...interfaces.formula import Formula

class Eq(Formula):
    """
    Equality formula.
    """

    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def apply_right(self, sequent):
        """
        Right rule for equality.

        Handles:
        - reflexivity
        - symmetry (if reversed equality is in context)
        - transitivity (if a = c and c = b are in context)
        - rewriting on either side
        """
        a = self.left
        b = self.right

        # reflexivity: ⊢ a = a
        if a == b:
            return ([], "bottom-left")

        # symmetry: Γ ⊢ a = b if Γ contains b = a
        if Eq(b, a) in sequent.antecedent:
            return ([], "bottom-left")

        # transitivity: Γ ⊢ a = b if Γ contains a = c and c = b
        for f in sequent.antecedent:
            if isinstance(f, Eq) and f.left == a:
                mid = f.right
                for g in sequent.antecedent:
                    if isinstance(g, Eq) and g.left == mid and g.right == b:
                        return ([], "bottom-left")

        # rewriting on left side
        new_left, rule = a.rewrite_once()
        if new_left is not None:
            after = Eq(new_left, b)
            new_seq = sequent.replace_right(after)
            new_seq.add_step(rule, a, new_left)
            return ([new_seq], "single")

        # rewriting on right side
        new_right, rule = b.rewrite_once()
        if new_right is not None:
            after = Eq(a, new_right)
            new_seq = sequent.replace_right(after)
            new_seq.add_step(rule, b, new_right)
            return ([new_seq], "single")

        return None

    def apply_left(self, sequent):
        """
        Left rule for equality: substitutivity in both directions.

        Only substitutes where the term actually occurs.
        """
        ant = sequent.antecedent
        succ = sequent.succedent

        # branch 1: substitute left → right
        ant1 = tuple(
            f.substitute(self.left, self.right) if f.occurs(self.left) else f
            for f in ant
        )
        succ1 = (
            succ.substitute(self.left, self.right)
            if succ.occurs(self.left)
            else succ
        )
        seq1 = sequent.with_antecedent(ant1).with_succedent(succ1)

        # branch 2: substitute right → left
        ant2 = tuple(
            f.substitute(self.right, self.left) if f.occurs(self.right) else f
            for f in ant
        )
        succ2 = (
            succ.substitute(self.right, self.left)
            if succ.occurs(self.right)
            else succ
        )
        seq2 = sequent.with_antecedent(ant2).with_succedent(succ2)

        return ([seq1, seq2], "multiple")

    def substitute(self, var, term):
        """
        Substitute inside both sides of the equality.
        """
        if self == var:
            return self
        return Eq(
            self.left.substitute(var, term),
            self.right.substitute(var, term),
        )

    def rewrite_once(self):
        """
        Try rewriting either side once.
        """
        new_left, rule = self.left.rewrite_once()
        if new_left is not None:
            return Eq(new_left, self.right), rule

        new_right, rule = self.right.rewrite_once()
        if new_right is not None:
            return Eq(self.left, new_right), rule

        return None, None

    def occurs(self, subterm):
        """
        Check if subterm occurs in either side of the equality.
        """
        return (
            self.left == subterm
            or self.right == subterm
            or self.left.occurs(subterm)
            or self.right.occurs(subterm)
        )

    def simplify(self):
        return Eq(self.left.simplify(), self.right.simplify())

    def __str__(self):
        return f"({self.left} = {self.right})"

    def __eq__(self, other):
        return (
            isinstance(other, Eq)
            and self.left == other.left
            and self.right == other.right
        )

    def __hash__(self):
        return hash(("eq", self.left, self.right))
