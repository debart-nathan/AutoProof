"""
Parser for logical formulas in standard mathematical notation.
"""

import re

# Logic formulas
from .formula.logic import (
    Atomic, Implication, Equivalence, Conjunction,
    Disjunction, Bottom, Negation, Universal, Existential
)

# Arithmetic / comparison formulas
from .formula.arithmetic import (
    Add, Sub, Mul, Div,
    Eq, NotEq, Lt, Gt, Le, Ge,
    Zero, Succ,
)

from .interfaces.parser_interface import ParserInterface


class Parser(ParserInterface):
    """
    Standard mathematical logic parser with arithmetic term support.
    """

    def __init__(self):
        self.tokens = []
        self.pos = 0

    # ============================================================
    # TOKENIZER (robust, regex-based)
    # ============================================================
    def tokenize(self, text):
        # Normalize unicode operators
        text = text.replace('∧', ' and ')
        text = text.replace('∨', ' or ')
        text = text.replace('¬', ' not ')
        text = text.replace('→', ' -> ')
        text = text.replace('↔', ' <-> ')
        text = text.replace('⊥', ' bottom ')
        text = text.replace('⊤', ' top ')
        text = text.replace('∀', ' forall ')
        text = text.replace('∃', ' exists ')

        token_spec = [
            (r'<->', '<->'),
            (r'->', '->'),
            (r'<=', '<='),
            (r'>=', '>='),
            (r'!=', '!='),
            (r'\(', '('),
            (r'\)', ')'),
            (r'\.', '.'),
            (r',', ','),
            (r'\+', '+'),
            (r'-', '-'),
            (r'\*', '*'),
            (r'/', '/'),
            (r'=', '='),
            (r'<', '<'),
            (r'>', '>'),
            (r'\bforall\b', 'forall'),
            (r'\bexists\b', 'exists'),
            (r'\band\b', 'and'),
            (r'\bor\b', 'or'),
            (r'\bnot\b', 'not'),
            (r'\bbottom\b', 'bottom'),
            (r'\btop\b', 'top'),
            (r'[0-9]+', 'NUMBER'),
            (r'[A-Za-z_][A-Za-z0-9_]*', 'IDENT'),
            (r'\s+', None),
        ]

        master = '|'.join(f'(?P<T{i}>{pat})' for i, (pat, _) in enumerate(token_spec))
        regex = re.compile(master)

        tokens = []
        for m in regex.finditer(text):
            for i, (_, value) in enumerate(token_spec):
                if m.lastgroup == f'T{i}':
                    if value is None:
                        break
                    if value in ('NUMBER', 'IDENT'):
                        tokens.append(m.group())
                    else:
                        tokens.append(value)
                    break

        self.tokens = tokens
        self.pos = 0

    # ============================================================
    # PARSE ENTRY
    # ============================================================
    def parse(self, text):
        self.tokenize(text)
        return self.equiv_expr()

    # ============================================================
    # FORMULA GRAMMAR
    # ============================================================
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
            var = self._expect_identifier("Expected variable after forall")
            self._expect('.')
            return Universal(var, self.equiv_expr())

        if self._accept('exists'):
            var = self._expect_identifier("Expected variable after exists")
            self._expect('.')
            return Existential(var, self.equiv_expr())

        return self.atom()

    # ============================================================
    # ATOMS (formulas, comparisons, terms)
    # ============================================================
    def atom(self):
        # Parenthesized expression: could be formula OR term
        if self._accept('('):
            expr = self.equiv_expr()
            self._expect(')')

            # If next token is a comparison operator, treat expr as a TERM
            if self._peek() in ('=', '!=', '<', '>', '<=', '>='):
                left = expr
                if self._accept('='):
                    return Eq(left, self.term_expr())
                if self._accept('!='):
                    return NotEq(left, self.term_expr())
                if self._accept('<'):
                    return Lt(left, self.term_expr())
                if self._accept('>'):
                    return Gt(left, self.term_expr())
                if self._accept('<='):
                    return Le(left, self.term_expr())
                if self._accept('>='):
                    return Ge(left, self.term_expr())

            return expr

        # bottom / top
        if self._accept('bottom'):
            return Bottom()
        if self._accept('top'):
            return Atomic("True")

        # IDENT or NUMBER → term or comparison
        if self._peek_is_identifier() or self._peek_is_number():
            left = self.term_expr()

            # comparison operators
            if self._accept('='):
                return Eq(left, self.term_expr())
            if self._accept('!='):
                return NotEq(left, self.term_expr())
            if self._accept('<'):
                return Lt(left, self.term_expr())
            if self._accept('>'):
                return Gt(left, self.term_expr())
            if self._accept('<='):
                return Le(left, self.term_expr())
            if self._accept('>='):
                return Ge(left, self.term_expr())

            return left

        raise ValueError(f"Unexpected token: {self._peek()}")

    # ============================================================
    # TERM GRAMMAR
    # ============================================================
    def term_expr(self):
        return self._parse_add()

    def _parse_add(self):
        left = self._parse_mul()
        while True:
            if self._accept('+'):
                left = Add(left, self._parse_mul())
            elif self._accept('-'):
                left = Sub(left, self._parse_mul())
            else:
                break
        return left

    def _parse_mul(self):
        left = self._parse_factor()
        while True:
            if self._accept('*'):
                left = Mul(left, self._parse_factor())
            elif self._accept('/'):
                left = Div(left, self._parse_factor())
            else:
                break
        return left

    def _parse_factor(self):
        tok = self._peek()

        # Parenthesized term
        if tok == '(':
            self._advance()
            expr = self.term_expr()
            self._expect(')')
            return expr

        # Number
        if self._peek_is_number():
            num = self._advance()
            if num == '0':
                return Zero()
            return Atomic(num)

        # Identifier or function term
        if self._peek_is_identifier():
            name = self._advance()

            # S(t) → Succ(t)
            if name == 'S' and self._accept('('):
                inner = self.term_expr()
                self._expect(')')
                return Succ(inner)

            # generic function-style term
            if self._accept('('):
                args = self._parse_term_list()
                self._expect(')')
                return Atomic(name, args)

            return Atomic(name)

        raise ValueError(f"Invalid term: {tok}")

    def _parse_term_list(self):
        args = []
        while True:
            args.append(self.term_expr())
            if not self._accept(','):
                break
        return args

    # ============================================================
    # TOKEN HELPERS
    # ============================================================
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
        return re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', tok) is not None

    def _peek_is_number(self):
        tok = self._peek()
        return tok is not None and tok.isdigit()

    def _expect_identifier(self, msg):
        if not self._peek_is_identifier():
            raise ValueError(msg)
        return self._advance()
