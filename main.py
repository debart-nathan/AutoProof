#!/usr/bin/env python3
from core.parser import Parser
from core.python_parser import PythonParser
from core.prover import Prover
from core.sequent import Sequent
from core.formula.logic import Atomic, Negation


def print_tree(node, indent=0):
    """Pretty-print a ProofNode tree."""
    print("  " * indent + f"{node.rule}: {node.sequent}")
    for p in node.premises:
        print_tree(p, indent + 1)


def check_sequent_status(prover, sequent):
    """
    Determine whether a sequent is proven, disproven, or unknown.
    IMPORTANT: does NOT overwrite the proof tree for the original sequent.
    """
    status, tree = prover._prove(sequent, 0)
    prover.last_proof_tree = tree  # preserve the original proof tree

    if status == "proven":
        return "proven"

    negated_seq = Sequent(sequent.antecedent, Negation(sequent.succedent))
    status_neg, _ = prover._prove(negated_seq, 0)

    if status_neg == "proven":
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
        seq = Sequent(ant, formula)
        status = check_sequent_status(prover, seq)
        print(f"\nProving {seq}: {status}")
        if prover.last_proof_tree:
            print_tree(prover.last_proof_tree)

    print("\n=== NON-PROVABLE / UNKNOWN SEQUENTS ===")
    tests = [
        ("¬A", []),
        ("A", []),
        ("¬¬A -> A", []),
        ("A ∨ ¬A", []),
        ("A ∧ ¬A", []),
    ]

    for text, ant in tests:
        formula = parser.parse(text)
        seq = Sequent(ant, formula)
        status = check_sequent_status(prover, seq)
        print(f"\nProving {seq}: {status}")
        if prover.last_proof_tree:
            print_tree(prover.last_proof_tree)

    print("\n=== EXPLOSION TESTS (Γ, ⊥ ⇒ anything) ===")
    A = Atomic("A")
    B = Atomic("B")
    notA = Negation(A)

    explosion_tests = [
        ([A, notA], B),
        ([notA], A),
    ]

    for ant, succ in explosion_tests:
        seq = Sequent(ant, succ)
        status = check_sequent_status(prover, seq)
        print(f"\nProving {seq}: {status}")
        if prover.last_proof_tree:
            print_tree(prover.last_proof_tree)

    print("\n=== DOUBLE NEGATION TESTS ===")
    dn_tests = [
        ([], Negation(Negation(A))),
        ([Negation(Negation(A))], A),
    ]

    for ant, succ in dn_tests:
        seq = Sequent(ant, succ)
        status = check_sequent_status(prover, seq)
        print(f"\nProving {seq}: {status}")
        if prover.last_proof_tree:
            print_tree(prover.last_proof_tree)

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
    status = check_sequent_status(prover, seq5)
    print(f"\nProving {seq5}: {status}")
    if prover.last_proof_tree:
        print_tree(prover.last_proof_tree)

    func_code2 = '''
def func2(x):
    for i in range(x):
        pass
    return True
'''
    formula6 = python_parser.parse_function(func_code2)
    seq6 = Sequent([], formula6)
    status = check_sequent_status(prover, seq6)
    print(f"\nProving {seq6}: {status}")
    if prover.last_proof_tree:
        print_tree(prover.last_proof_tree)

    print("\n=== DIRECT SANITY CHECK ===")
    seq_direct = Sequent([], Negation(A))
    status = prover.prove(seq_direct)
    print(f"\nDIRECT TEST {seq_direct}: {status}")
    if prover.last_proof_tree:
        print_tree(prover.last_proof_tree)


if __name__ == "__main__":
    main()
