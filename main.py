#!/usr/bin/env python3
"""
Comprehensive test suite for the AutoProof intuitionistic prover.
"""

import core
from core.parser import Parser
from core.python_parser import PythonParser
from core.prover import Prover
from core.sequent import Sequent
from core.formula.logic import Atomic, Negation
from core.formula.arithmetic import Add, Eq, Succ, Zero


def print_tree(node, indent=0):
    """Pretty-print a ProofNode tree."""
    print("  " * indent + f"{node.rule}: {node.sequent}")
    for p in node.premises:
        print_tree(p, indent + 1)


def run_tests(prover, tests, title):
    """Run a list of (antecedent, succedent) tests under a section title."""
    print(f"\n=== {title} ===")
    for ant, succ in tests:
        seq = Sequent(ant, succ)
        status = prover.prove(seq)
        print(f"\nProving {seq}: {status}")
        if prover.last_proof_tree:
            print_tree(prover.last_proof_tree)


def main():
    parser = Parser()
    python_parser = PythonParser()
    prover = Prover()

    # ----------------------------------------------------------------------
    # BASIC INTUITIONISTIC VALIDITIES
    # ----------------------------------------------------------------------
    basic_tests = [
        ([], parser.parse("A -> A")),
        ([], parser.parse("(A ∧ B) -> A")),
        ([], parser.parse("A -> (B -> A)")),
        ([], parser.parse("A -> ¬¬A")),
        ([], parser.parse("¬A -> (A -> ⊥)")),
        ([], parser.parse("A <-> A")),
        ([], parser.parse("forall x. (P(x) -> P(x))")),
    ]

    run_tests(prover, basic_tests, "BASIC INTUITIONISTIC VALIDITIES")

    # ----------------------------------------------------------------------
    # NON-PROVABLE / UNKNOWN SEQUENTS
    # ----------------------------------------------------------------------
    nonprovable_tests = [
        ([], parser.parse("¬A")),
        ([], parser.parse("A")),
        ([], parser.parse("¬¬A -> A")),
        ([], parser.parse("A ∨ ¬A")),
        ([], parser.parse("A ∧ ¬A")),
    ]

    run_tests(prover, nonprovable_tests, "NON-PROVABLE / UNKNOWN SEQUENTS")

    # ----------------------------------------------------------------------
    # EXPLOSION TESTS
    # ----------------------------------------------------------------------
    A = Atomic("A")
    B = Atomic("B")
    notA = Negation(A)

    explosion_tests = [
        ([A, notA], B),
        ([notA], A),
    ]

    run_tests(prover, explosion_tests, "EXPLOSION TESTS (Γ, ⊥ ⇒ anything)")

    # ----------------------------------------------------------------------
    # DOUBLE NEGATION TESTS
    # ----------------------------------------------------------------------
    dn_tests = [
        ([], Negation(Negation(A))),
        ([Negation(Negation(A))], A),
    ]

    run_tests(prover, dn_tests, "DOUBLE NEGATION TESTS")

    # ----------------------------------------------------------------------
    # ARITHMETIC ADDITION TESTS (parsed)
    # ----------------------------------------------------------------------
    arithmetic_tests = [
        ([], parser.parse("S(0) + 0 = S(0)")),
        ([], parser.parse("S(0) + S(0) = S(S(0))")),
        ([], parser.parse("(S(S(0)) + 0) = S(S(0))")),
    ]

    run_tests(prover, arithmetic_tests, "ARITHMETIC ADDITION TESTS")

    # ----------------------------------------------------------------------
    # EQUALITY THEORY TESTS (parsed)
    # ----------------------------------------------------------------------
    equality_tests = [
        ([], parser.parse("a = a")),                     # reflexivity
        ([parser.parse("b = a")], parser.parse("a = b")),  # symmetry
        ([parser.parse("a = b"), parser.parse("b = c")],
         parser.parse("a = c")),                         # transitivity
    ]

    run_tests(prover, equality_tests, "EQUALITY THEORY TESTS")

    # ----------------------------------------------------------------------
    # PYTHON PARSER TESTS
    # ----------------------------------------------------------------------
    func_code = '''
def func(x):
    y = x + 1
    if y > 0:
        return True
    else:
        return False
'''
    func_formula = python_parser.parse_function(func_code)

    func_code2 = '''
def func2(x):
    for i in range(x):
        pass
    return True
'''
    func_formula2 = python_parser.parse_function(func_code2)

    python_tests = [
        ([], func_formula),
        ([], func_formula2),
    ]

    run_tests(prover, python_tests, "PYTHON PARSER TESTS")

    # ----------------------------------------------------------------------
    # DIRECT SANITY CHECK
    # ----------------------------------------------------------------------
    run_tests(prover, [([], Negation(A))], "DIRECT SANITY CHECK")


if __name__ == "__main__":
    main()
