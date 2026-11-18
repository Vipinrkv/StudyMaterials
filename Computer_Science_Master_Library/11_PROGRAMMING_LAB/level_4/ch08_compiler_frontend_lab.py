"""
Level 4 Chapter 08 Programming Lab: Compiler Frontend (Lexing, CFGs & Parsing)
=============================================================================
Focus: Lexical Analysis, FIRST & FOLLOW set mathematical computation,
       and hand-written Recursive Descent AST Parser with evaluation.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from typing import List, Dict, Set, Tuple, Optional, Any
import re


# ---------------------------------------------------------------------------
# 1. Lexical Analysis (Scanner / Tokenizer)
# ---------------------------------------------------------------------------

class TokenType:
    NUMBER = "NUMBER"
    IDENT = "IDENT"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    ASSIGN = "ASSIGN"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    SEMICOLON = "SEMICOLON"
    EOF = "EOF"


class Token:
    def __init__(self, token_type: str, value: Any, line: int, col: int):
        self.type = token_type
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"


class Lexer:
    TOKEN_SPECS = [
        ("NUMBER", r"\d+(\.\d+)?"),
        ("IDENT", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("PLUS", r"\+"),
        ("MINUS", r"-"),
        ("MUL", r"\*"),
        ("DIV", r"/"),
        ("ASSIGN", r"="),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("SEMICOLON", r";"),
        ("SKIP", r"[ \t]+"),
        ("NEWLINE", r"\n"),
    ]

    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self._tokenize()

    def _tokenize(self):
        regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in self.TOKEN_SPECS)
        line = 1
        line_start = 0

        for match in re.finditer(regex, self.source):
            kind = match.lastgroup
            val = match.group()
            col = match.start() - line_start + 1

            if kind == "NUMBER":
                num_val = float(val) if "." in val else int(val)
                self.tokens.append(Token(TokenType.NUMBER, num_val, line, col))
            elif kind == "IDENT":
                self.tokens.append(Token(TokenType.IDENT, val, line, col))
            elif kind == "PLUS":
                self.tokens.append(Token(TokenType.PLUS, val, line, col))
            elif kind == "MINUS":
                self.tokens.append(Token(TokenType.MINUS, val, line, col))
            elif kind == "MUL":
                self.tokens.append(Token(TokenType.MUL, val, line, col))
            elif kind == "DIV":
                self.tokens.append(Token(TokenType.DIV, val, line, col))
            elif kind == "ASSIGN":
                self.tokens.append(Token(TokenType.ASSIGN, val, line, col))
            elif kind == "LPAREN":
                self.tokens.append(Token(TokenType.LPAREN, val, line, col))
            elif kind == "RPAREN":
                self.tokens.append(Token(TokenType.RPAREN, val, line, col))
            elif kind == "SEMICOLON":
                self.tokens.append(Token(TokenType.SEMICOLON, val, line, col))
            elif kind == "NEWLINE":
                line += 1
                line_start = match.end()
            elif kind == "SKIP":
                pass

        self.tokens.append(Token(TokenType.EOF, "", line, len(self.source) - line_start + 1))


# ---------------------------------------------------------------------------
# 2. FIRST and FOLLOW Sets Mathematical Computation Engine
# ---------------------------------------------------------------------------

Grammar = Dict[str, List[List[str]]]

def compute_first_sets(grammar: Grammar, terminals: Set[str], non_terminals: Set[str]) -> Dict[str, Set[str]]:
    first: Dict[str, Set[str]] = {nt: set() for nt in non_terminals}
    for t in terminals:
        first[t] = {t}
    first["ε"] = {"ε"}

    changed = True
    while changed:
        changed = False
        for A, productions in grammar.items():
            for prod in productions:
                # Production of form A -> X1 X2 ... Xk
                if prod == ["ε"]:
                    if "ε" not in first[A]:
                        first[A].add("ε")
                        changed = True
                    continue

                all_derive_epsilon = True
                for symbol in prod:
                    sym_first = first.get(symbol, {symbol})
                    for f in sym_first:
                        if f != "ε" and f not in first[A]:
                            first[A].add(f)
                            changed = True
                    if "ε" not in sym_first:
                        all_derive_epsilon = False
                        break

                if all_derive_epsilon and "ε" not in first[A]:
                    first[A].add("ε")
                    changed = True

    return {k: v for k, v in first.items() if k in non_terminals}


def compute_follow_sets(grammar: Grammar, start_symbol: str, terminals: Set[str], non_terminals: Set[str], first: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    follow: Dict[str, Set[str]] = {nt: set() for nt in non_terminals}
    follow[start_symbol].add("$")

    changed = True
    while changed:
        changed = False
        for A, productions in grammar.items():
            for prod in productions:
                if prod == ["ε"]:
                    continue
                for i, B in enumerate(prod):
                    if B in non_terminals:
                        # Beta is rest of production after B
                        beta = prod[i + 1:]
                        if beta:
                            # FIRST(beta)
                            all_beta_epsilon = True
                            for sym in beta:
                                sym_first = first.get(sym, {sym})
                                for f in sym_first:
                                    if f != "ε" and f not in follow[B]:
                                        follow[B].add(f)
                                        changed = True
                                if "ε" not in sym_first:
                                    all_beta_epsilon = False
                                    break
                            if all_beta_epsilon:
                                for f in follow[A]:
                                    if f not in follow[B]:
                                        follow[B].add(f)
                                        changed = True
                        else:
                            # B is at the very end: A -> alpha B
                            for f in follow[A]:
                                if f not in follow[B]:
                                    follow[B].add(f)
                                    changed = True

    return follow


# ---------------------------------------------------------------------------
# 3. Recursive Descent AST Parser
# ---------------------------------------------------------------------------

class ASTNode:
    pass

class NumberNode(ASTNode):
    def __init__(self, value: float):
        self.value = value

    def __repr__(self):
        return f"Num({self.value})"

class VariableNode(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Var({self.name})"

class BinaryOpNode(ASTNode):
    def __init__(self, op: str, left: ASTNode, right: ASTNode):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"

class AssignNode(ASTNode):
    def __init__(self, var_name: str, expr: ASTNode):
        self.var_name = var_name
        self.expr = expr

    def __repr__(self):
        return f"Assign({self.var_name} = {self.expr})"


class RecursiveDescentParser:
    """
    Grammar (stratified to enforce operator precedence):
      statement  -> IDENT '=' expr ';'
      expr       -> term ( ('+' | '-') term )*
      term       -> factor ( ('*' | '/') factor )*
      factor     -> NUMBER | IDENT | '(' expr ')'
    """
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current_token(self) -> Token:
        return self.tokens[self.pos]

    def consume(self, expected_type: str) -> Token:
        tok = self.current_token()
        if tok.type != expected_type:
            raise SyntaxError(f"Expected token {expected_type}, got {tok.type} at line {tok.line}:{tok.col}")
        self.pos += 1
        return tok

    def parse_statement(self) -> AssignNode:
        ident_tok = self.consume(TokenType.IDENT)
        self.consume(TokenType.ASSIGN)
        expr_node = self.parse_expr()
        self.consume(TokenType.SEMICOLON)
        return AssignNode(ident_tok.value, expr_node)

    def parse_expr(self) -> ASTNode:
        node = self.parse_term()
        while self.current_token().type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self.current_token()
            self.pos += 1
            right = self.parse_term()
            node = BinaryOpNode(op_tok.value, node, right)
        return node

    def parse_term(self) -> ASTNode:
        node = self.parse_factor()
        while self.current_token().type in (TokenType.MUL, TokenType.DIV):
            op_tok = self.current_token()
            self.pos += 1
            right = self.parse_factor()
            node = BinaryOpNode(op_tok.value, node, right)
        return node

    def parse_factor(self) -> ASTNode:
        tok = self.current_token()
        if tok.type == TokenType.NUMBER:
            self.pos += 1
            return NumberNode(tok.value)
        elif tok.type == TokenType.IDENT:
            self.pos += 1
            return VariableNode(tok.value)
        elif tok.type == TokenType.LPAREN:
            self.pos += 1
            node = self.parse_expr()
            self.consume(TokenType.RPAREN)
            return node
        else:
            raise SyntaxError(f"Unexpected token {tok} at line {tok.line}:{tok.col}")


def evaluate_ast(node: ASTNode, env: Dict[str, float]) -> float:
    if isinstance(node, NumberNode):
        return node.value
    elif isinstance(node, VariableNode):
        if node.name not in env:
            raise NameError(f"Undefined variable '{node.name}'")
        return env[node.name]
    elif isinstance(node, BinaryOpNode):
        l_val = evaluate_ast(node.left, env)
        r_val = evaluate_ast(node.right, env)
        if node.op == "+":
            return l_val + r_val
        elif node.op == "-":
            return l_val - r_val
        elif node.op == "*":
            return l_val * r_val
        elif node.op == "/":
            return l_val / r_val
    elif isinstance(node, AssignNode):
        val = evaluate_ast(node.expr, env)
        env[node.var_name] = val
        return val
    raise ValueError(f"Unknown AST node type {type(node)}")


def test_compiler_frontend_suite():
    print("[TEST 1] Lexical Analysis of Assignment Statement...")
    source = "total = (base_price + 15) * 2;"
    lexer = Lexer(source)
    tok_types = [t.type for t in lexer.tokens]
    expected_types = [
        TokenType.IDENT, TokenType.ASSIGN, TokenType.LPAREN,
        TokenType.IDENT, TokenType.PLUS, TokenType.NUMBER,
        TokenType.RPAREN, TokenType.MUL, TokenType.NUMBER,
        TokenType.SEMICOLON, TokenType.EOF
    ]
    assert tok_types == expected_types, f"Token mismatch: {tok_types}"
    print(f"  -> Successfully scanned {len(lexer.tokens)} tokens with accurate source spans.")

    print("[TEST 2] FIRST and FOLLOW Sets Calculation...")
    # Grammar:
    # E  -> T E'
    # E' -> + T E' | ε
    # T  -> F T'
    # T' -> * F T' | ε
    # F  -> ( E ) | id
    grammar = {
        "E": [["T", "E_prime"]],
        "E_prime": [["+", "T", "E_prime"], ["ε"]],
        "T": [["F", "T_prime"]],
        "T_prime": [["*", "F", "T_prime"], ["ε"]],
        "F": [["(", "E", ")"], ["id"]],
    }
    terminals = {"+", "*", "(", ")", "id"}
    non_terminals = {"E", "E_prime", "T", "T_prime", "F"}

    first = compute_first_sets(grammar, terminals, non_terminals)
    follow = compute_follow_sets(grammar, "E", terminals, non_terminals, first)

    assert "(" in first["E"] and "id" in first["E"], "FIRST(E) computation incorrect"
    assert "$" in follow["E"] and ")" in follow["E"], "FOLLOW(E) computation incorrect"
    print(f"  -> FIRST(E): {first['E']}, FOLLOW(E): {follow['E']} verified.")

    print("[TEST 3] Recursive Descent AST Parsing & Evaluation...")
    parser = RecursiveDescentParser(lexer.tokens)
    ast = parser.parse_statement()
    
    env = {"base_price": 35.0}
    result = evaluate_ast(ast, env)
    # Expected: (35 + 15) * 2 = 100.0
    assert result == 100.0, f"Expected 100.0, got {result}"
    assert env["total"] == 100.0, f"Variable total not stored properly in environment"
    print(f"  -> AST built: {ast}")
    print(f"  -> Execution evaluated result: total = {env['total']} (Verified)")

    print("ALL Level 4 Chapter 08 Compiler Frontend lab tests passed successfully!")


if __name__ == "__main__":
    test_compiler_frontend_suite()
