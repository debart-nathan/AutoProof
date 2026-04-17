"""Prover using natural deduction rules for intuitionistic logic."""

from typing import Literal, List, Tuple, Optional
from .checker import Checker
from .sequent import Sequent
from .interfaces.prover_interface import ProverInterface
from .proof_node import ProofNode

ProofStatus = Literal["proven", "disproven", "unknown"]


class Prover(ProverInterface):
    """
    Natural deduction prover for intuitionistic logic.
    
    Uses memoization to avoid re-proving identical sequents.
    Implements LJT (Focused Intuitionistic Logic) transformations.
    """
    def __init__(self, max_depth: int = 100):
        self.max_depth = max_depth
        self.memo: dict[Sequent, Tuple[ProofStatus, Optional[ProofNode]]] = {}
        self.last_proof_tree: Optional[ProofNode] = None

    def prove(self, sequent, depth: int = 0) -> ProofStatus:
        """Prove a sequent using natural deduction."""
        status, node = self._prove(sequent, depth)
        self.last_proof_tree = node
        return status

    def reset_memo(self) -> None:
        """Clear memoization cache."""
        self.memo = {}
        self.last_proof_tree = None

    def _prove(
        self,
        sequent,
        depth: int,
    ) -> Tuple[ProofStatus, Optional[ProofNode]]:
        if depth > self.max_depth:
            return "unknown", None
        
        
        if isinstance(sequent, tuple):
            sequent = Sequent(sequent[0], sequent[1])

        # Memo lookup (Sequent has proper __hash__ and __eq__)
        if sequent in self.memo:
            return self.memo[sequent]

        # Axiom rule: if succedent is in context
        if sequent.contains_in_context(sequent.succedent):
            node = ProofNode(sequent=sequent, rule="axiom", premises=[])
            result = ("proven", node)
            self.memo[sequent] = result
            return result

        result_right = sequent.succedent.apply_right(sequent)
        if result_right is not None:
            premises, conn_type = result_right
            ok, subnodes = self._handle_premises(premises, conn_type, depth)
            if ok:
                node = ProofNode(
                    sequent=sequent,
                    rule=f"R:{type(sequent.succedent).__name__}",
                    premises=subnodes,
                )
                result = ("proven", node)
                self.memo[sequent] = result
                return result

        for formula in sequent.antecedent:
            result_left = formula.apply_left(sequent)
            if result_left is not None:
                premises, conn_type = result_left
                ok, subnodes = self._handle_premises(premises, conn_type, depth)
                if ok:
                    node = ProofNode(
                        sequent=sequent,
                        rule=f"L:{type(formula).__name__}",
                        premises=subnodes,
                    )
                    result = ("proven", node)
                    self.memo[sequent] = result
                    return result

        result = ("unknown", None)
        self.memo[sequent] = result
        return result

    def _handle_premises(
        self,
        premises,
        conn_type: str,
        depth: int,
    ) -> Tuple[bool, List[ProofNode]]:
        if conn_type == "bottom-left":
            return True, []

        if conn_type == "none":
            return False, []

        if conn_type == "single":
            status, node = self._prove(premises[0], depth + 1)
            if status == "proven" and node is not None:
                return True, [node]
            return False, []

        if conn_type in ("and", "multiple"):
            subnodes: List[ProofNode] = []
            for p in premises:
                status, node = self._prove(p, depth + 1)
                if status != "proven" or node is None:
                    return False, []
                subnodes.append(node)
            return True, subnodes

        if conn_type == "or":
            for p in premises:
                status, node = self._prove(p, depth + 1)
                if status == "proven" and node is not None:
                    return True, [node]
            return False, []

        return False, []
