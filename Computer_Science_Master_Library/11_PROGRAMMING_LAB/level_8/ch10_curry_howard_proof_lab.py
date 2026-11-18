"""
ch10_curry_howard_proof_lab.py
Level 8 Chapter 10 Companion Laboratory: Interactive Theorem Proving & Type Checking.
Implements Constructive Propositional Logic, Simply-Typed Lambda Calculus,
and a Certified Proof-Term Type Checker demonstrating the Curry-Howard Isomorphism.
Pure Python/Standard Library with zero external dependencies.
"""

from __future__ import annotations
import sys
from typing import Dict, List, Tuple, Optional, Any

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8")


class Prop:
    """Base class for Constructive Mathematical Propositions."""
    pass

class Atom(Prop):
    def __init__(self, name: str):
        self.name = name
    def __repr__(self) -> str:
        return self.name
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Atom) and self.name == other.name

class Implies(Prop):
    """Implication Proposition: A -> B"""
    def __init__(self, src: Prop, dst: Prop):
        self.src = src
        self.dst = dst
    def __repr__(self) -> str:
        return f"({self.src} -> {self.dst})"
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Implies) and self.src == other.src and self.dst == other.dst

class And(Prop):
    """Conjunction Proposition: A /\\ B"""
    def __init__(self, left: Prop, right: Prop):
        self.left = left
        self.right = right
    def __repr__(self) -> str:
        return f"({self.left} /\\ {self.right})"
    def __eq__(self, other: object) -> bool:
        return isinstance(other, And) and self.left == other.left and self.right == other.right


# ==============================================================================
# PROOF TERMS (LAMBDA CALCULUS AST)
# ==============================================================================

class ProofTerm:
    pass

class Var(ProofTerm):
    def __init__(self, name: str):
        self.name = name
    def __repr__(self) -> str:
        return self.name

class Lam(ProofTerm):
    """Lambda Abstraction: \\x : T . body (Implication Introduction)"""
    def __init__(self, var_name: str, var_type: Prop, body: ProofTerm):
        self.var_name = var_name
        self.var_type = var_type
        self.body = body
    def __repr__(self) -> str:
        return f"(\\{self.var_name}:{self.var_type}. {self.body})"

class App(ProofTerm):
    """Function Application: e1 e2 (Modus Ponens / Implication Elimination)"""
    def __init__(self, func: ProofTerm, arg: ProofTerm):
        self.func = func
        self.arg = arg
    def __repr__(self) -> str:
        return f"({self.func} {self.arg})"

class Pair(ProofTerm):
    """Pair Constructor: <e1, e2> (Conjunction Introduction)"""
    def __init__(self, left: ProofTerm, right: ProofTerm):
        self.left = left
        self.right = right
    def __repr__(self) -> str:
        return f"<{self.left}, {self.right}>"

class Fst(ProofTerm):
    """First Projection: fst(p) (Conjunction Elimination Left)"""
    def __init__(self, pair: ProofTerm):
        self.pair = pair
    def __repr__(self) -> str:
        return f"fst({self.pair})"

class Snd(ProofTerm):
    """Second Projection: snd(p) (Conjunction Elimination Right)"""
    def __init__(self, pair: ProofTerm):
        self.pair = pair
    def __repr__(self) -> str:
        return f"snd({self.pair})"


class CurryHowardProofChecker:
    """Type-checking kernel certifying formal proof terms against propositions."""
    @classmethod
    def type_check(cls, term: ProofTerm, context: Dict[str, Prop]) -> Prop:
        if isinstance(term, Var):
            if term.name not in context:
                raise TypeError(f"Unbound hypothesis variable: '{term.name}'")
            return context[term.name]

        elif isinstance(term, Lam):
            new_ctx = dict(context)
            new_ctx[term.var_name] = term.var_type
            body_type = cls.type_check(term.body, new_ctx)
            return Implies(term.var_type, body_type)

        elif isinstance(term, App):
            func_type = cls.type_check(term.func, context)
            if not isinstance(func_type, Implies):
                raise TypeError(f"Attempted to apply non-implication proof term of type: {func_type}")
            arg_type = cls.type_check(term.arg, context)
            if func_type.src != arg_type:
                raise TypeError(f"Type mismatch: expected {func_type.src}, got {arg_type}")
            return func_type.dst

        elif isinstance(term, Pair):
            t_left = cls.type_check(term.left, context)
            t_right = cls.type_check(term.right, context)
            return And(t_left, t_right)

        elif isinstance(term, Fst):
            p_type = cls.type_check(term.pair, context)
            if not isinstance(p_type, And):
                raise TypeError(f"fst requires conjunction type, got {p_type}")
            return p_type.left

        elif isinstance(term, Snd):
            p_type = cls.type_check(term.pair, context)
            if not isinstance(p_type, And):
                raise TypeError(f"snd requires conjunction type, got {p_type}")
            return p_type.right

        raise TypeError(f"Unknown proof term AST: {type(term)}")


def main() -> None:
    print("=" * 70)
    print("LEVEL 8 CHAPTER 10: CURRY-HOWARD THEOREM PROVER LAB")
    print("=" * 70)

    A = Atom("A")
    B = Atom("B")
    C = Atom("C")

    # 1. Theorem 1: Identity (A -> A)
    print("\n[Test 1] Certifying Theorem: A -> A (Identity Law)...")
    proof_id = Lam("x", A, Var("x"))
    derived_type_1 = CurryHowardProofChecker.type_check(proof_id, {})
    expected_type_1 = Implies(A, A)
    assert derived_type_1 == expected_type_1
    print(f"  -> Proof Term: {proof_id}")
    print(f"  -> Certified Type: {derived_type_1} (Q.E.D.)")

    # 2. Theorem 2: Conjunction Commutativity ((A /\\ B) -> (B /\\ A))
    print("\n[Test 2] Certifying Theorem: (A /\\ B) -> (B /\\ A)...")
    # \\p : (A /\\ B) . <snd(p), fst(p)>
    hyp = And(A, B)
    proof_comm = Lam("p", hyp, Pair(Snd(Var("p")), Fst(Var("p"))))
    derived_type_2 = CurryHowardProofChecker.type_check(proof_comm, {})
    expected_type_2 = Implies(And(A, B), And(B, A))
    assert derived_type_2 == expected_type_2
    print(f"  -> Proof Term: {proof_comm}")
    print(f"  -> Certified Type: {derived_type_2} (Q.E.D.)")

    # 3. Theorem 3: Modus Ponens ((A -> B) -> A -> B)
    print("\n[Test 3] Certifying Theorem: (A -> B) -> A -> B (Modus Ponens)...")
    # \\f : (A -> B) . \\x : A . f x
    proof_mp = Lam("f", Implies(A, B), Lam("x", A, App(Var("f"), Var("x"))))
    derived_type_3 = CurryHowardProofChecker.type_check(proof_mp, {})
    expected_type_3 = Implies(Implies(A, B), Implies(A, B))
    assert derived_type_3 == expected_type_3
    print(f"  -> Proof Term: {proof_mp}")
    print(f"  -> Certified Type: {derived_type_3} (Q.E.D.)")

    # 4. Negative Test: Erroneous Proof Rejection
    print("\n[Test 4] Testing Type Checker Kernel Rejection of Bogus Proof...")
    # Attempt to prove A -> B via identity (\\x:A . x)
    invalid_term = Lam("x", A, Var("x"))
    bogus_claim = Implies(A, B)
    actual_type = CurryHowardProofChecker.type_check(invalid_term, {})
    assert actual_type != bogus_claim, "Kernel must not certify invalid proof!"
    print(f"  -> Attempted Proof Type: {actual_type} != Claimed: {bogus_claim}.")
    print("  -> Unsound Proof Rejection: VERIFIED (Kernel Integrity Intact).")

    print("\n" + "=" * 70)
    print("ALL CURRY-HOWARD PROOF CHECKING TESTS PASSED (Exit Code 0).")
    print("=" * 70)
    sys.exit(0)


if __name__ == "__main__":
    main()
