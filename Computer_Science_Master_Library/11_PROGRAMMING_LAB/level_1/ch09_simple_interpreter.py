"""
Practical Lab 1.9: Educational Mini-Interpreter & AST Evaluator
File: 11_PROGRAMMING_LAB/level_1/ch09_simple_interpreter.py
Author: Computer Science Master Library
Description: Demonstrates the foundational phases of a programming language runtime:
             Lexical Tokenization, Parsing, Symbol Table Management, and Execution.
"""

import sys
import re
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class Token:

    def __init__(self, type_: str, value: Any):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"


def tokenize(source_code: str) -> List[Token]:
    """LEXICAL ANALYSIS: Converts raw string characters into structured tokens."""
    token_specification = [
        ("NUMBER", r"\d+"),
        ("PRINT", r"\bPRINT\b"),
        ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),
        ("ASSIGN", r"="),
        ("PLUS", r"\+"),
        ("MINUS", r"-"),
        ("MULTIPLY", r"\*"),
        ("SKIP", r"[ \t]+"),
        ("NEWLINE", r"\n"),
    ]
    tok_regex = "|".join(
        f"(?P<{pair[0]}>{pair[1]})" for pair in token_specification
    )
    tokens: List[Token] = []

    for mo in re.finditer(tok_regex, source_code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == "NUMBER":
            tokens.append(Token("NUMBER", int(value)))
        elif kind == "SKIP" or kind == "NEWLINE":
            continue
        elif kind in (
            "PRINT",
            "IDENTIFIER",
            "ASSIGN",
            "PLUS",
            "MINUS",
            "MULTIPLY",
        ):
            tokens.append(Token(kind, value))
        else:
            raise SyntaxError(f"Unexpected character: {value}")

    return tokens


class SimpleInterpreter:
    """INTERPRETER & EXECUTION ENGINE: Evaluates tokens against a Symbol Table."""

    def __init__(self):
        self.symbol_table: Dict[str, int] = {}

    def execute(self, tokens: List[Token]) -> None:
        idx = 0
        n = len(tokens)

        while idx < n:
            tok = tokens[idx]

            # Case 1: Assignment Statement -> IDENTIFIER = EXPRESSION
            if (
                tok.type == "IDENTIFIER"
                and (idx + 1 < n)
                and tokens[idx + 1].type == "ASSIGN"
            ):
                var_name = tok.value
                idx += 2

                val = self._evaluate_value(tokens[idx])
                idx += 1

                if idx < n and tokens[idx].type in (
                    "PLUS",
                    "MINUS",
                    "MULTIPLY",
                ):
                    op = tokens[idx].type
                    idx += 1
                    rhs = self._evaluate_value(tokens[idx])
                    idx += 1
                    if op == "PLUS":
                        val += rhs
                    elif op == "MINUS":
                        val -= rhs
                    elif op == "MULTIPLY":
                        val *= rhs

                self.symbol_table[var_name] = val
                print(
                    f"[Runtime] Assigned: {var_name} = {val} (Symbol Table Updated)"
                )

            # Case 2: PRINT statement -> PRINT IDENTIFIER
            elif tok.type == "PRINT":
                idx += 1
                target = tokens[idx]
                idx += 1
                result = self._evaluate_value(target)
                print(f">>> OUTPUT: {result}")

            else:
                idx += 1

    def _evaluate_value(self, token: Token) -> int:
        if token.type == "NUMBER":
            return token.value
        elif token.type == "IDENTIFIER":
            if token.value in self.symbol_table:
                return self.symbol_table[token.value]
            else:
                raise NameError(
                    f"Runtime Error: Variable '{token.value}' is referenced before assignment!"
                )
        raise SyntaxError(f"Expected number or identifier, got {token}")


if __name__ == "__main__":
    program_code = """
    apples = 10
    bonus = 5
    total = apples + bonus
    PRINT total
    reward = total * 2
    PRINT reward
    """

    print("=" * 60)
    print("        RUNNING MINI-LANGUAGE COMPILER PIPELINE")
    print("=" * 60)
    print("Source Code:\n", program_code)

    token_stream = tokenize(program_code)
    print("--- Phase 1: Generated Token Stream ---")
    for t in token_stream:
        print(f"  {t}")
    print()

    print("--- Phase 2: Execution & Output ---")
    runtime = SimpleInterpreter()
    runtime.execute(token_stream)

    assert runtime.symbol_table["apples"] == 10
    assert runtime.symbol_table["bonus"] == 5
    assert runtime.symbol_table["total"] == 15
    assert runtime.symbol_table["reward"] == 30
    print("\nAll interpreter simulation tests passed successfully.")
