#!/usr/bin/env python3
from core.Parser import Parser
from core.PythonParser import PythonParser
from core.Prover import Prover
from core.Sequent import Sequent
from core.logic.Atomic import Atomic
from core.logic.Implication import Implication
from core.logic.Equivalence import Equivalence
from core.logic.Negation import Negation


def check_sequent_status(prover, sequent):
    result = prover.prove(sequent)
    if result == "proven":
        return "proven"
    # For unprovable check, negate the succedent
    if isinstance(sequent, Sequent):
        negated_seq = Sequent(sequent.antecedent, Negation(sequent.succedent))
    else:
        negated_seq = (sequent[0], Negation(sequent[1]))
    if prover.prove(negated_seq) == "proven":
        return "disproven"
    return "unknown"


def main():
    parser = Parser()
    python_parser = PythonParser()
    prover = Prover()

    print("\n=== BASIC INTUITIONISTIC VALIDITIES ===")
    tests = [
        ("A -> A", []),
        ("(A ∧ B) -> A", []),
        ("A -> (B -> A)", []),
        ("A -> ¬¬A", []),
        ("¬A -> (A -> ⊥)", []),
        ("A <-> A", []),
        ("forall x. (P x -> P x)", []),
    ]

    for text, ant in tests:
        formula = parser.parse(text)
        seq = Sequent(ant, formula)  # Use Sequent class
        print(f"Proving {seq}: {check_sequent_status(prover, seq)}")

    print("\n=== NON-PROVABLE / UNKNOWN SEQUENTS ===")
    tests = [
        ("¬A", []),               # should be unknown
        ("A", []),                # not provable
        ("¬¬A -> A", []),         # not intuitionistically valid
        ("A ∨ ¬A", []),           # LEM not provable
        ("A ∧ ¬A", []),           # contradiction
    ]

    for text, ant in tests:
        formula = parser.parse(text)
        seq = Sequent(ant, formula)
        print(f"Proving {seq}: {check_sequent_status(prover, seq)}")

    print("\n=== EXPLOSION TESTS (Γ, ⊥ ⇒ anything) ===")
    A = Atomic("A")
    B = Atomic("B")
    notA = Negation(A)

    explosion_tests = [
        ([A, notA], B),           # A, ¬A ⇒ B  should be provable
        ([notA], A),              # ¬A ⇒ A     unknown
    ]

    for ant, succ in explosion_tests:
        seq = Sequent(ant, succ)
        print(f"Proving {seq}: {check_sequent_status(prover, seq)}")

    print("\n=== DOUBLE NEGATION TESTS ===")
    dn_tests = [
        ([], Negation(Negation(A))),   # ⇒ ¬¬A  provable
        ([Negation(Negation(A))], A),  # ¬¬A ⇒ A unknown
    ]

    for ant, succ in dn_tests:
        seq = Sequent(ant, succ)
        print(f"Proving {seq}: {check_sequent_status(prover, seq)}")

    print("\n=== PYTHON PARSER TESTS ===")

    func_code = '''
def func(x):
    y = x + 1
    if y > 0:
        return True
    else:
        return False
'''
    formula5 = python_parser.parse_function(func_code)
    seq5 = Sequent([], formula5)
    print(f"Proving {seq5}: {check_sequent_status(prover, seq5)}")

    func_code2 = '''
def func2(x):
    for i in range(x):
        pass
    return True
'''
    formula6 = python_parser.parse_function(func_code2)
    seq6 = Sequent([], formula6)
    print(f"Proving {seq6}: {check_sequent_status(prover, seq6)}")

    print("\n=== DIRECT SANITY CHECK ===")
    seq_direct = Sequent([], Negation(A))
    print(f"DIRECT TEST {seq_direct}: {prover.prove(seq_direct)}")


if __name__ == "__main__":
    main()
