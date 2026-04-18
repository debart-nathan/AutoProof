"""
Parser for logical formulas in standard mathematical notation.
"""

import re

# Logic formulas
from .formula.logic import (
    Atomic, Implication, Equivalence, Conjunction,
    Disjunction, Bottom, Negation, Universal, Existential
)

# Arithmetic formulas
from .formula.arithmetic import (
    Add, Sub, Mul, Div,
    Eq, NotEq, Lt, Gt, Le, Ge
)

from .interfaces.parser_interface import ParserInterface


class Parser(ParserInterface):
    """
    Standard mathematical logic parser with arithmetic term support.
    """

    def __init__(self):
        self.tokens = []
        self.pos = 0

    # -----------------------------
    # TOKEN PROCESSING
    # -----------------------------
    def tokenize(self, text):
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
            '<==>' : ' <-> ',
        }
        for k, v in ascii_ops.items():
            text = text.replace(k, v)

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

        text = (
            text.replace('(', ' ( ')
                .replace(')', ' ) ')
                .replace('.', ' . ')
                .replace(',', ' , ')
        )

        spaced_ops = ['forall', 'exists', 'and', 'or', 'not', '->', '<->']
        for op in spaced_ops:
            pattern = rf'\b{re.escape(op)}\b'
            text = re.sub(pattern, f' {op} ', text)

        self.tokens = [t for t in text.split() if t]
        self.pos = 0

    # -----------------------------
    # PARSE ENTRY
    # -----------------------------
    def parse(self, text):
        self.tokenize(text)
        return self.equiv_expr()

    # -----------------------------
    # FORMULA GRAMMAR
    # -----------------------------
    def equiv_expr(self):
        left = self.impl_expr()
        while self._accept('<->'):
            right = self.impl_expr()
            left = Equivalence(left, right)
        return left

    def impl_expr(self):
        left = self.or_expr()
        if self._accept('->'):
            right = self.impl_expr()
            return Implication(left, right)
        return left

    def or_expr(self):
        left = self.and_expr()
        while self._accept('or'):
            right = self.and_expr()
            left = Disjunction(left, right)
        return left

    def and_expr(self):
        left = self.unary_expr()
        while self._accept('and'):
            right = self.unary_expr()
            left = Conjunction(left, right)
        return left

    def unary_expr(self):
        if self._accept('not'):
            return Negation(self.unary_expr())
        return self.quantifier_expr()

    def quantifier_expr(self):
        if self._accept('forall'):
            var = self._expect_identifier('Expected variable after forall')
            self._expect('.')
            body = self.unary_expr()
            return Universal(var, body)

        if self._accept('exists'):
            var = self._expect_identifier('Expected variable after exists')
            self._expect('.')
            body = self.unary_expr()
            return Existential(var, body)

        return self.atom()

    # -----------------------------
    # ATOMS AND TERMS
    # -----------------------------
    def atom(self):
        if self._accept('('):
            expr = self.equiv_expr()
            self._expect(')')
            return expr

        if self._accept('bottom'):
            return Bottom()

        if self._accept('top'):
            return Atomic("True")

        if self._peek_is_identifier():
            name = self._advance()

            # Function-style: P(x, y)
            if self._accept('('):
                args = self._parse_term_list()
                self._expect(')')
                return Atomic(name, args)

            # Application-style: P x y
            args = []
            while self._peek_is_identifier():
                args.append(self._parse_term())

            if args:
                return Atomic(name, args)

            return Atomic(name)

        raise ValueError(f"Unexpected token: {self._peek()}")

    # -----------------------------
    # TERM PARSING
    # -----------------------------
    def _parse_term(self):
        """Parse arithmetic terms."""
        tok = self._peek()

        # Parenthesized term
        if tok == '(':
            self._advance()
            term = self._parse_term()
            self._expect(')')
            return term

        # Variable or constant
        if self._peek_is_identifier():
            name = self._advance()
            return Atomic(name)

        raise ValueError(f"Invalid term: {tok}")

    def _parse_term_list(self):
        args = []
        while True:
            args.append(self._parse_term())
            if not self._accept(','):
                break
        return args

    # -----------------------------
    # TOKEN HELPERS
    # -----------------------------
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
            raise ValueError(f"Expected '{token}', got '{self._peek()}'")

    def _peek_is_identifier(self):
        tok = self._peek()
        if tok is None:
            return False
        if tok in {
            'and', 'or', 'not', '->', '<->',
            'forall', 'exists',
            'bottom', 'top',
            '(', ')', '.', ',', 
        }:
            return False
        return re.match(r'^[^\(\),]+$', tok) is not None

    def _expect_identifier(self, msg):
        if not self._peek_is_identifier():
            raise ValueError(msg)
        return self._advance()
