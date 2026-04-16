import re
from .logic.Atomic import Atomic
from .logic.Implication import Implication
from .logic.Equivalence import Equivalence
from .logic.Conjunction import Conjunction
from .logic.Disjunction import Disjunction
from .logic.Bottom import Bottom
from .logic.Negation import Negation
from .logic.Universal import Universal
from .logic.Existential import Existential


class Parser:
    def __init__(self):
        self.tokens = []
        self.pos = 0

    # ------------------------------------------------------------
    # SUPER-FORGIVING TOKENIZER
    # ------------------------------------------------------------
    def tokenize(self, text):
        # 1. Normalize common ASCII operator variants
        ascii_ops = {
            '&&': ' and ',
            '&': ' and ',
            '||': ' or ',
            '|': ' or ',
            '!': ' not ',
            '~': ' not ',
            '=>': ' -> ',
            '==>': ' -> ',
            '<=>': ' <-> ',
            '<==>': ' <-> ',
        }
        for k, v in ascii_ops.items():
            text = text.replace(k, v)

        # 2. Normalize Unicode operators (optional sugar)
        unicode_ops = {
            '∧': ' and ',
            '∨': ' or ',
            '¬': ' not ',
            '→': ' -> ',
            '↔': ' <-> ',
            '⊥': ' bottom ',
            '⊤': ' top ',
            '∀': ' forall ',
            '∃': ' exists ',
        }
        for k, v in unicode_ops.items():
            text = text.replace(k, v)

        # 3. Add spacing around parentheses and dots
        text = (
            text.replace('(', ' ( ')
                .replace(')', ' ) ')
                .replace('.', ' . ')
        )

        # 4. Ensure core ASCII operators are spaced
        spaced_ops = ['and', 'or', 'not', '->', '<->', 'forall', 'exists']
        for op in spaced_ops:
            text = text.replace(op, f' {op} ')

        # 5. Final split
        self.tokens = [t for t in text.split() if t]
        self.pos = 0

    # ------------------------------------------------------------
    # ENTRY POINT
    # ------------------------------------------------------------
    def parse(self, text):
        self.tokenize(text)
        result = self.equiv_expr()
        # ignore trailing junk instead of failing hard
        return result

    # ------------------------------------------------------------
    # GRAMMAR IMPLEMENTATION
    # ------------------------------------------------------------
    def equiv_expr(self):
        left = self.impl_expr()
        while self._accept("<->"):
            right = self.impl_expr()
            left = Equivalence(left, right)
        return left

    def impl_expr(self):
        left = self.or_expr()
        if self._accept("->"):
            right = self.impl_expr()
            return Implication(left, right)
        return left

    def or_expr(self):
        left = self.and_expr()
        while self._accept("or"):
            right = self.and_expr()
            left = Disjunction(left, right)
        return left

    def and_expr(self):
        left = self.unary_expr()
        while self._accept("and"):
            right = self.unary_expr()
            left = Conjunction(left, right)
        return left

    # ------------------------------------------------------------
    # UNARY + QUANTIFIERS
    # ------------------------------------------------------------
    def unary_expr(self):
        if self._accept("not"):
            return Negation(self.unary_expr())
        return self.quantifier_expr()

    def quantifier_expr(self):
        if self._accept("forall"):
            var = self._expect_identifier("Expected variable after 'forall'")
            self._expect(".")
            body = self.unary_expr()
            return Universal(var, body)

        if self._accept("exists"):
            var = self._expect_identifier("Expected variable after 'exists'")
            self._expect(".")
            body = self.unary_expr()
            return Existential(var, body)

        return self.atom()

    # ------------------------------------------------------------
    # ATOMS + TERMS
    # ------------------------------------------------------------
    def atom(self):
        if self._accept("("):
            expr = self.equiv_expr()
            self._expect(")")
            return expr

        if self._accept("bottom"):
            return Bottom()

        if self._accept("top"):
            return Atomic("True")

        if self._peek_is_identifier():
            name = self._advance()

            # Predicate application: P(...)
            if self._accept("("):
                args = self._parse_term_list()
                self._expect(")")
                return Atomic(f"{name}({', '.join(args)})")

            # Propositional atom
            return Atomic(name)

        raise ValueError(f"Unexpected token: {self._peek()}")

    # ------------------------------------------------------------
    # TERM LIST PARSER
    # ------------------------------------------------------------
    def _parse_term_list(self):
        args = []
        current = []
        depth = 0

        while True:
            tok = self._peek()
            if tok is None:
                raise ValueError("Unclosed term list")

            if tok == "(":
                depth += 1
                current.append(self._advance())
            elif tok == ")":
                if depth == 0:
                    break
                depth -= 1
                current.append(self._advance())
            elif tok == "," and depth == 0:
                self._advance()
                args.append(" ".join(current))
                current = []
            else:
                current.append(self._advance())

        args.append(" ".join(current))
        return args

    # ------------------------------------------------------------
    # TOKEN HELPERS
    # ------------------------------------------------------------
    def _peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _advance(self):
        tok = self._peek()
        if tok is None:
            raise ValueError("Unexpected end of input")
        self.pos += 1
        return tok

    def _accept(self, token):
        if self._peek() == token:
            self.pos += 1
            return True
        return False

    def _expect(self, token):
        if not self._accept(token):
            # soft: just return, caller may handle inconsistencies
            return

    def _peek_is_identifier(self):
        tok = self._peek()
        return tok is not None and re.match(r'^[^\(\),]+$', tok)

    def _expect_identifier(self, msg):
        tok = self._peek()
        if tok is None or not re.match(r'^[^\(\),]+$', tok):
            raise ValueError(msg)
        return self._advance()
