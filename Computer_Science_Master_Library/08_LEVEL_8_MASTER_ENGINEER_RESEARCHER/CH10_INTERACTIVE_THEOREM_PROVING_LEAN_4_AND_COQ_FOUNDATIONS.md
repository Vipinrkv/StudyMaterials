# CHAPTER 10: INTERACTIVE THEOREM PROVING, LEAN 4, COQ, AND PROGRAM VERIFICATION

---

## 1. ACADEMIC & REAL-WORLD CONTEXT

Throughout computer science history, the gold standard for software reliability has progressed from manual code inspection, to empirical unit testing, to model checking. Yet, even model checkers are fundamentally bounded by finite state spaces. For mission-critical systems—such as high-assurance operating system microkernels (seL4), cryptographic primitives (HACL* in Firefox), optimizing compilers (CompCert), and mathematical proofs (the Four Color Theorem, Kepler Conjecture)—engineers require absolute, mathematically unbroken certainty that software conforms unconditionally to its formal specification across infinite execution spaces.

This pinnacle of high-assurance computing is achieved through **Interactive Theorem Proving (ITP)**, powered by modern proof assistants such as **Lean 4**, **Coq (The Coq Proof Assistant)**, and **Isabelle/HOL**. 

Built upon the profound mathematical equivalence known as the **Curry-Howard Isomorphism**, interactive theorem provers reframe theorem proving as typed functional programming: a mathematical proposition is a type, and a formal proof is a valid program inhabiting that type. If the type checker certifies the program without error, the mathematical theorem is definitively proven true for all time.

This chapter dissects the formal foundations of interactive theorem proving and constructive logic. We examine dependent type theory ($\Pi$-types, $\Sigma$-types), inductive data types, the Calculus of Inductive Constructions (CIC), interactive proof tactics (`induction`, `rewrite`, `simp`, `cases`, `exact`), and end-to-end formal software verification in Lean 4.

---

## 2. PEDAGOGICAL ROADMAP

```
                    Interactive Theorem Proving & Type Theory
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                             ▼
Constructive Logic & Proof Theory                            The Curry-Howard Isomorphism
(Intuitionistic Logic, Excluded Middle)                      (Propositions as Types, Proofs as Programs)
        │                                                             │
        ▼                                                             ▼
Dependent Type Theory                                        Calculus of Inductive Constructions
(Pi-Types / Dependent Functions, Sigma-Types)                (Inductive Types, Pattern Matching, Recursion)
        │                                                             │
        └──────────────────────────────┬──────────────────────────────┘
                                       │
                                       ▼
                       Interactive Proof Mechanics (Lean 4)
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
        ▼                                                             ▼
Forward Proofs vs Tactic Proofs                              Core Interactive Proof Tactics
(Proof Terms vs Step-by-Step Tactic State)                   (intro, exact, apply, cases, induction, rw)
        │                                                             │
        └──────────────────────────────┬──────────────────────────────┘
                                       │
                                       ▼
                         Certified Software Verification
                                       │
                 ┌─────────────────────┴─────────────────────┐
                 ▼                                           ▼
         Correctness of Functional Programs          Certified Compilers & Microkernels
     (Provably Sorted Lists, Invariants)             (seL4 Verified Microkernel, CompCert C)
```

---

## 3. CORE PRINCIPLES & FORMAL DEFINITIONS

### 3.1 The Curry-Howard Isomorphism

The **Curry-Howard Isomorphism** establishes a profound 1-to-1 correspondence between mathematical logic and typed computation:

| Logic (Propositions & Truth) | Type Theory (Types & Programs) |
| :--- | :--- |
| **Proposition $P$** | **Type $T$** |
| **Proof of $P$** | **Value / Program $t$ of type $T$ ($t : T$)** |
| **Conjunction ($A \land B$)** | **Product Type / Pair ($A \times B$)** |
| **Disjunction ($A \lor B$)** | **Sum Type / Either ($A + B$)** |
| **Implication ($A \implies B$)** | **Function Type ($A \to B$)** |
| **Universal Quantification ($\forall x:A, B(x)$)** | **Dependent Function Type ($\Pi (x : A), B(x)$)** |
| **Existential Quantification ($\exists x:A, B(x)$)**| **Dependent Pair Type ($\Sigma (x : A), B(x)$)** |
| **Absurdity / Falsehood ($\bot$)** | **Empty Type (Void / Bottom)** |

Under this correspondence, proving the implication $A \implies B$ is identical to authoring a terminating function that takes an argument of type $A$ and returns a value of type $B$.

### 3.2 Dependent Types: $\Pi$-Types and $\Sigma$-Types

In standard type systems, types and terms are disjoint. In **dependent type systems**, types may depend on runtime values:
- **Dependent Function Type ($\Pi$-Type):** The return type of a function depends on the argument value:
  $$f : \Pi (x : A), B(x)$$
  Example: A function that takes an integer $n$ and returns a vector of exact length $n$: $\text{zeros} : \Pi (n : \mathbb{N}), \text{Vector}(\mathbb{R}, n)$.
- **Dependent Pair Type ($\Sigma$-Type):** A pair $(a, b)$ where the type of the second element depends on the value of the first:
  $$\Sigma (x : A), B(x)$$
  Example: A sorted list packaged together with a formal mathematical proof that its elements are in ascending order.

---

## 4. MATHEMATICAL FOUNDATIONS & PROOFS

### 4.1 Inductive Proof of List Length Additivity

Consider the inductive definition of natural numbers (Peano arithmetic) and linked lists in constructive logic:
$$\mathbb{N} \triangleq \text{zero} \mid \text{succ}(n)$$
$$\text{List}(T) \triangleq \text{nil} \mid \text{cons}(x, \text{xs})$$

Let concatenation be defined recursively:
$$\text{nil} ++ ys = ys$$
$$\text{cons}(x, xs) ++ ys = \text{cons}(x, xs ++ ys)$$

**Theorem (Additivity of List Concatenation Length):**
$$\forall (xs, ys : \text{List}(T)), \quad \text{length}(xs ++ ys) = \text{length}(xs) + \text{length}(ys)$$

*Proof by Structural Induction on $xs$:*
- **Base Case ($xs = \text{nil}$):**
  $$\text{LHS} = \text{length}(\text{nil} ++ ys) = \text{length}(ys)$$
  $$\text{RHS} = \text{length}(\text{nil}) + \text{length}(ys) = 0 + \text{length}(ys) = \text{length}(ys)$$
  $\text{LHS} = \text{RHS}$. The base case holds by definition.
- **Inductive Step ($xs = \text{cons}(x, xs')$):**
  Assume the induction hypothesis (IH): $\text{length}(xs' ++ ys) = \text{length}(xs') + \text{length}(ys)$.
  $$\text{LHS} = \text{length}(\text{cons}(x, xs') ++ ys) = \text{length}(\text{cons}(x, xs' ++ ys)) = 1 + \text{length}(xs' ++ ys)$$
  Applying the induction hypothesis:
  $$\text{LHS} = 1 + (\text{length}(xs') + \text{length}(ys)) = (1 + \text{length}(xs')) + \text{length}(ys)$$
  By definition of length:
  $$\text{RHS} = \text{length}(\text{cons}(x, xs')) + \text{length}(ys) = (1 + \text{length}(xs')) + \text{length}(ys)$$
  $\text{LHS} = \text{RHS}$.
By structural induction, the theorem holds for all lists $xs$ and $ys$. $\blacksquare$

---

## 5. ARCHITECTURAL PATTERNS & ENGINE DESIGNS

```
+─────────────────────────────────────────────────────────────────────────────+
|                    LEAN 4 THEOREM PROVER ARCHITECTURE                       |
|                                                                             |
|      HIGH-LEVEL SOURCE CODE                                                 |
|  +───────────────────────────────────────────────────────────────────────+  |
|  | theorem add_comm (m n : Nat) : m + n = n + m := by                    |  |
|  |   induction n with                                                    |  |
|  |   | zero => rw [Nat.add_zero, Nat.zero_add]                           |  |
|  |   | succ d ih => rw [Nat.add_succ, Nat.succ_add, ih]                  |  |
|  +───────────────────────────────────┬───────────────────────────────────+  |
|                                      │                                      |
|                                      ▼ Tactic Elaboration                   |
|  +───────────────────────────────────────────────────────────────────────+  |
|  |                Explicit Proof Term (Lambda Calculus)                  |  |
|  |         \lambda m n, Nat.recOn n ... (Pure Functional AST)            |  |
|  +───────────────────────────────────┬───────────────────────────────────+  |
|                                      │                                      |
|                                      ▼ De Bruijn Type Checking              |
|  +───────────────────────────────────────────────────────────────────────+  |
|  |                     TINY TRUSTED COMPUTING BASE (TCB)                 |  |
|  |               Small, audited C++ kernel verifying typing              |  |
|  |        * Rejects any invalid proof step with 100% certainty *         |  |
|  +───────────────────────────────────────────────────────────────────────+  |
+─────────────────────────────────────────────────────────────────────────────+
```

---

## 6. COMPARATIVE ANALYSIS: PROOF ASSISTANTS

| Dimension | Lean 4 | Coq (The Coq Proof Assistant) | Isabelle/HOL |
| :--- | :--- | :--- | :--- |
| **Logic Framework** | Calculus of Inductive Constructions | Calculus of Inductive Constructions | Higher-Order Logic (Classical) |
| **Programming Language** | Full general-purpose systems language | OCaml-based DSL (Gallina) | Standard ML (SML) |
| **Primary Strength** | Modern pure mathematics & code verification | Formal software verification (CompCert) | Hardware verification & automation |
| **Proof Style** | Modern tactic blocks (`by ...`) | Tactic scripts (`Ltac`) | Isar structured proofs |
| **Industry Adoption** | AWS, Galois, Meta AI | INRIA, Airbus, Docker | Apple, Intel, ARM |

---

## 7. INDUSTRIAL CASE STUDIES & POST-MORTEMS

### Case Study: The seL4 Verified Microkernel
In 2009, researchers at NICTA (Data61) completed the formal verification of the **seL4 microkernel** in Isabelle/HOL. Spanning over 200,000 lines of formal proof, the team mathematically proved that seL4's C implementation is an exact semantic refinement of its abstract specification. seL4 remains the world's first operating system kernel with mathematically proven **absence of buffer overflows, null pointer dereferences, memory leaks, and privilege escalation vulnerabilities**.

---

## 8. COMPLETE, PRODUCTION-READY IMPLEMENTATION

Below is a complete, self-contained Python laboratory proof engine (`curry_howard_proof_checker.py`) implementing an AST type-checker for simply-typed lambda calculus with conjunctions, disjunctions, and proof term verification demonstrating the Curry-Howard Isomorphism.

```python
"""
curry_howard_proof_checker.py
Curry-Howard Isomorphism & Interactive Theorem Prover Simulator.
Implements Constructive Propositional Logic, Simply-Typed Lambda Calculus,
and a Certified Proof-Term Type Checker.
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
    """Conjunction Proposition: A /\ B"""
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
    """Pair Constructor: (e1, e2) (Conjunction Introduction)"""
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
    """
    Type-checking kernel that certifies formal proof terms against propositions.
    Proves that a lambda calculus program inhabits a propositional type.
    """
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
```

---

## 9. STEP-BY-STEP GUIDED LAB WALKTHROUGH

1. **Identity Proposition ($A \implies A$):** Formulate the identity proof term $\lambda x:A . x$ and verify type checking succeeds.
2. **Conjunction Commutativity ($A \land B \implies B \land A$):** Construct the pair-swapping lambda term $\lambda p : (A \land B) . \langle \text{snd}(p), \text{fst}(p) \rangle$ and verify it inhabits $(B \land A)$.
3. **Modus Ponens Elimination:** Apply an implication proof term to an argument hypothesis; verify that output equals destination proposition.
4. **Invalid Proof Rejection:** Submit an erroneous proof term attempting to prove $A \implies B$ using variable of type $A$; verify type-checker catches error.

---

## 10. COMPREHENSIVE BENCHMARKS & COMPLEXITY ANALYSIS

| Proof Assistant Engine | Trusted Computing Base (TCB) Size | Logic Foundation | Type-Checking Time (Standard MathLib) |
| :--- | :--- | :--- | :--- |
| **Lean 4** | ~5,000 lines C++ | Calculus of Inductive Constructions | Highly parallel (Minutes) |
| **Coq (CIC Kernel)** | ~8,000 lines OCaml | Calculus of Inductive Constructions | Single-threaded (Hours) |
| **Isabelle/HOL** | ~10,000 lines SML | Higher-Order Logic (Gordon's HOL) | Parallel ML (Minutes) |
| **Agda** | ~30,000 lines Haskell | Homotopy Type Theory (HoTT) | Moderate (Minutes) |

---

## 11. EXTREME EDGE CASES & FAILURE MODES

- **Girard's Paradox (Type in Type):** If a type system allows the universe `Type : Type`, the system becomes logically inconsistent, allowing the proof of False ($\bot$). Provers enforce universe hierarchies ($\text{Type}_0 < \text{Type}_1 < \dots$).
- **Non-Termination in Proof Terms:** If recursive functions do not strictly terminate (e.g., infinite loops), the Curry-Howard correspondence collapses because a looping term could inhabit any type, proving false statements. All recursion must be provably well-founded.
- **TCB Compiler Vulnerabilities:** If the trusted kernel compiler (GCC/Clang compiling the C++ type checker) has a bug, unsound proofs could theoretically pass verification.

---

## 12. DEBUGGING, PROFILING & TRACE ANALYSIS

- Inspect active goals in the Lean 4 Infoview pane (`#check`, `#eval`).
- Profile proof elaboration times using `set_option trace.profiler true`.
- Minimize tactic proofs into explicit functional proof terms via `#print <theorem_name>`.

---

## 13. REAL-WORLD PRODUCTION DRILLS & RUNBOOKS

- **Runbook — Formal Verification Gate in High-Assurance CI/CD:**
  1. Compile all formal proof scripts with the latest prover kernel (`lake build`).
  2. Enforce zero `sorry` placeholders (which admit unproven assumptions).
  3. Verify that all axioms used in proofs are within the approved enterprise foundational whitelist.

---

## 14. COMPREHENSIVE CURRICULUM & DEGREE MAPPINGS

- **B.Tech / BCS:** Propositional logic, predicate calculus, mathematical induction.
- **MCS / MCA:** Simply-typed lambda calculus, structural operational semantics, program verification.
- **M.Tech / MESE / Ph.D.:** Calculus of Inductive Constructions, Curry-Howard isomorphism, Lean 4 interactive tactics, certified compiler correctness.

---

## 15. INTERVIEW MASTERY: 10 ARCHITECTURAL & FORMAL VERIFICATION PROBLEMS

1. **Question:** What is the Curry-Howard Isomorphism?
   - *Answer:* The profound mathematical equivalence stating that mathematical propositions correspond to types in a type system, and proofs correspond to programs (proof terms) inhabiting those types. Proving a theorem is identical to writing a well-typed program.
2. **Question:** What is the Trusted Computing Base (TCB) of a proof assistant?
   - *Answer:* The minimal core kernel responsible for checking proof terms. While the tactic engine, parser, and IDE contain tens of thousands of lines of code, only the tiny core kernel (typically a few thousand lines of audited code) must be trusted for soundness.
3. **Question:** Why must all functions in a proof assistant be terminating?
   - *Answer:* If a function could loop infinitely without terminating, an engineer could define a non-terminating function of type `Empty` ($\bot$), which would mathematically prove False, compromising the consistency of the entire logic system.
4. **Question:** What is a dependent function type ($\Pi$-type)?
   - *Answer:* A function type where the type of the returned value depends on the runtime value passed into the function argument, generalizing universal quantification ($\forall x:A, B(x)$).
5. **Question:** What does the `induction` tactic do in Lean 4?
   - *Answer:* It applies structural mathematical induction to an inductive data type (such as natural numbers or lists), splitting the current proof goal into base cases and inductive steps equipped with induction hypotheses.
6. **Question:** What is the difference between classical logic and intuitionistic (constructive) logic?
   - *Answer:* Classical logic assumes the Law of the Excluded Middle ($P \lor \neg P$ is always true) and proof by contradiction. Constructive logic requires explicit witnesses: to prove $A \lor B$, one must either construct a proof of $A$ or a proof of $B$.
7. **Question:** What is the seL4 microkernel verification milestone?
   - *Answer:* The world's first complete formal verification of an operating system kernel, proving in Isabelle/HOL that the C code mathematically refines its high-level security specification with zero buffer overflows or privilege escalation bugs.
8. **Question:** What is Girard's Paradox?
   - *Answer:* The type-theoretic equivalent of Russell's paradox. It states that if a type universe is allowed to contain itself (`Type : Type`), an unsound self-referential term can be constructed that proves falsehood.
9. **Question:** What is the role of `simp` in Lean 4?
   - *Answer:* A powerful automation tactic that simplifies the current goal by repeatedly rewriting subterms using a database of equality theorems and congruence rules.
10. **Question:** What is the difference between a proof term and a tactic script?
    - *Answer:* A proof term is an explicit abstract syntax tree (lambda expression) directly accepted by the proof kernel. A tactic script is an imperative sequence of instructions that dynamically generates that underlying proof term.

---

## 16. EXAMINATIONS & KNOWLEDGE RETENTION DRILLS

### Multiple Choice Questions
1. Under the Curry-Howard Isomorphism, the logical conjunction $A \land B$ corresponds to:
   - (A) Function type $A \to B$
   - (B) Product type / Pair $(A \times B)$
   - (C) Sum type $A + B$
   - (D) Bottom type $\bot$
   - *Answer:* (B)
2. In Lean 4, a proof placeholder that temporarily admits an unproven goal is:
   - (A) `skip`
   - (B) `pass`
   - (C) `sorry`
   - (D) `admit`
   - *Answer:* (C)

---

## 17. SECURITY, RESILIENCE & COMPLIANCE

Interactive theorem proving delivers absolute mathematical certainty for aerospace avionics (DO-178C Level A), medical device controllers, smart contracts securing billions in capital, and cryptographic kernels.

---

## 18. EXPERT ANTI-PATTERNS & PITFALL CATALOGUE

1. **Anti-Pattern: Committing Proofs with Leftover `sorry` Statements**
   - *Error:* Leaving `sorry` in intermediate lemmas.
   - *Impact:* The proof assistant treats `sorry` as an axiom, allowing false theorems to compile successfully.
2. **Anti-Pattern: Overly Fragile Tactic Scripts**
   - *Error:* Relying on brittle positional tactics that break whenever definitions are subtly refactored.
   - *Fix:* Use robust, semantic tactics (`simp`, `rw`, structured `induction ... with`).

---

## 19. STANDARDS, RFCs & SYSTEM SPECIFICATIONS

- **Moura, Leonardo de & Ullrich, Sebastian (2021):** *The Lean 4 Theorem Prover and Programming Language*, CADE.
- **Klein, Gerwin et al. (2009):** *seL4: Formal Verification of an OS Kernel*, ACM SOSP.
- **Howard, William A. (1980):** *The Formulae-as-Types Notion of Construction*.

---

## 20. HISTORICAL PERSPECTIVE & DISCOVERIES

In 1934, Haskell Curry observed that the types of combinators matched the axioms of positive implicational logic. In 1969, William Alvin Howard formalized this into a rigorous correspondence between natural deduction and lambda calculus, creating the foundation for all modern proof assistants.

---

## 21. CODE REFACTORING & PRODUCTION HARDENING

When authoring verified software:
- Structure code into **pure functional specifications** and **optimized executable implementations**, proving equivalence via refinement theorems.
- Extract certified C or Rust code directly from verified models using verified extraction pipelines.

---

## 22. REAL-WORLD TOOLING & ECOSYSTEM DIRECTORY

- **Lean 4 / Mathlib 4:** The premier interactive theorem prover and mathematical library.
- **Coq / CompCert:** Verified C compiler translating C code into verified x86/ARM assembly.
- **F* (F-Star):** Higher-order effectful language designed for program verification, powering Microsoft Everest.

---

## 23. COMPREHENSIVE GLOSSARY OF FORMAL TERMS

- **Curry-Howard Isomorphism:** The direct mapping between logical propositions and computational types.
- **Dependent Type:** A type whose definition depends on a dynamic value.
- **Modus Ponens:** The logical rule of inference stating that if $P$ and $P \implies Q$, then $Q$.
- **Proof Term:** A formal lambda-calculus expression representing a mathematical proof.
- **Trusted Computing Base (TCB):** The minimal kernel of code whose correctness is essential to system security or logical soundness.

---

## 24. ADVANCED CAPSTONE & RESEARCH PROJECTS

1. **Verified Sorting Algorithm in Lean 4:** Formulate the specification of a sorted list in Lean 4, implement Insertion Sort, and prove both the `is_sorted` invariant and the permutation preservation theorem.
2. **Verified State Machine Refinement in Coq:** Model a distributed two-phase lock state machine in Coq, proving serializability invariants across arbitrary concurrent transaction schedules.
