"""
Parser for logical formulas in standard mathematical notation.
"""

import re
from .formulas import (
    Atomic, Implication, Equivalence, Conjunction,
    Disjunction, Bottom, Negation, Universal, Existential
)
from .interfaces.parser_interface import ParserInterface


class Parser(ParserInterface):
    """
    Standard mathematical logic parser.

    Supports standard logic notation:
    - Operators: and, or, not, ->, <->, forall, exists, bottom
    - Unicode: ∧, ∨, ¬, →, ↔, ⊥, ∀, ∃
    """
    def __init__(self):
        self.tokens = []
        self.pos = 0

    # TOKEN PROCESSING
    def tokenize(self, text):
        # Normalize common ASCII operator variants
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

        # Normalize Unicode operators
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

        # Add spacing around parentheses and dots
        text = (
            text.replace('(', ' ( ')
                .replace(')', ' ) ')
                .replace('.', ' . ')
        )

        # Ensure core ASCII operators are spaced
        spaced_ops = ['and', 'or', 'not', '->', '<->', 'forall', 'exists']
        for op in spaced_ops:
            text = text.replace(op, f' {op} ')

        self.tokens = [t for t in text.split() if t]
        self.pos = 0

    def parse(self, text):
        self.tokenize(text)
        result = self.equiv_expr()
        return result

    # GRAMMAR IMPLEMENTATION
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

    def atom(self):
        if self._accept('('):
            expr = self.equiv_expr()
            self._expect(')')
            return expr

        if self._accept('bottom'):
            return Bottom()

        if self._accept('top'):
            return Atomic('True')

        if self._peek_is_identifier():
            name = self._advance()

            if self._accept('('):
                args = self._parse_term_list()
                self._expect(')')
                return Atomic(f"{name}({', '.join(args)})")

            return Atomic(name)

        raise ValueError(f"Unexpected token: {self._peek()}")

    def _parse_term_list(self):
        args = []
        current = []
        depth = 0

        while True:
            tok = self._peek()
            if tok is None:
                raise ValueError("Unclosed term list")

            if tok == '(':
                depth += 1
                current.append(self._advance())
            elif tok == ')':
                if depth == 0:
                    break
                depth -= 1
                current.append(self._advance())
            elif tok == ',' and depth == 0:
                self._advance()
                args.append(' '.join(current))
                current = []
            else:
                current.append(self._advance())

        args.append(' '.join(current))
        return args

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
            return

    def _peek_is_identifier(self):
        tok = self._peek()
        return tok is not None and re.match(r'^[^\(\),]+$', tok)

    def _expect_identifier(self, msg):
        tok = self._peek()
        if tok is None or not re.match(r'^[^\(\),]+$', tok):
            raise ValueError(msg)
        return self._advance()
