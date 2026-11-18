# -*- coding: utf-8 -*-
"""
CH09: Testing at Scale (Unit, Integration, Contract, E2E) Lab
============================================================
Covers:
1. Gerard Meszaros Test Doubles Taxonomy (Dummy, Stub, Spy, Mock, Fake).
2. Mutation Testing Engine with AST/Operator Mutation and Mutation Score Calculator.
3. Consumer-Driven Contract Testing Validator (Pact-style schema verification).
"""
import sys
import ast
import copy
from typing import Any, Callable, Dict, List, Optional, Tuple

sys.stdout.reconfigure(encoding="utf-8")


# ============================================================================
# Section 1: Meszaros Test Doubles Taxonomy
# ============================================================================

class DummyLogger:
    """Dummy: Object passed around to satisfy signature but never used."""
    def log(self, message: str) -> None:
        pass


class StubExchangeRateService:
    """Stub: Provides canned, predetermined answers to calls."""
    def __init__(self, fixed_rate: float):
        self.fixed_rate = fixed_rate

    def get_rate(self, base_currency: str, target_currency: str) -> float:
        return self.fixed_rate


class SpyNotificationService:
    """Spy: Records invocation metadata (method, arguments, call count) for test verification."""
    def __init__(self):
        self.call_history: List[Tuple[str, Tuple[Any, ...], Dict[str, Any]]] = []

    def send_sms(self, phone: str, text: str) -> bool:
        self.call_history.append(("send_sms", (phone, text), {}))
        return True

    def was_called_with(self, phone: str, text: str) -> bool:
        return any(args == (phone, text) for name, args, _ in self.call_history)

    @property
    def call_count(self) -> int:
        return len(self.call_history)


class MockPaymentGateway:
    """Mock: Pre-programmed with strict expectations and verifies adherence."""
    def __init__(self):
        self.expected_calls: List[Tuple[str, Tuple[Any, ...]]] = []
        self.actual_calls: List[Tuple[str, Tuple[Any, ...]]] = []

    def expect(self, method_name: str, *args) -> 'MockPaymentGateway':
        self.expected_calls.append((method_name, args))
        return self

    def charge(self, user_id: str, amount: float) -> bool:
        self.actual_calls.append(("charge", (user_id, amount)))
        return True

    def verify(self) -> bool:
        if self.expected_calls != self.actual_calls:
            raise AssertionError(f"Mock verification failed!\nExpected: {self.expected_calls}\nActual:   {self.actual_calls}")
        return True


class FakeDatabaseRepository:
    """Fake: Fully functioning working implementation unsuitable for production (in-memory dict)."""
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def save(self, key: str, record: Dict[str, Any]) -> None:
        self._store[key] = copy.deepcopy(record)

    def find_by_id(self, key: str) -> Optional[Dict[str, Any]]:
        return copy.deepcopy(self._store.get(key))

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None


# ============================================================================
# Section 2: AST Mutation Testing Engine
# ============================================================================

class MutationVisitor(ast.NodeTransformer):
    """Generates syntactic mutants by mutating comparison, arithmetic, and boolean operators."""
    def __init__(self, mutation_id: int):
        self.target_mutation_id = mutation_id
        self.current_mutation_idx = 0
        self.applied = False

    def visit_Compare(self, node: ast.Compare) -> ast.AST:
        self.generic_visit(node)
        new_ops = []
        for op in node.ops:
            if self.current_mutation_idx == self.target_mutation_id and not self.applied:
                # Mutate operator
                if isinstance(op, ast.Lt):
                    new_ops.append(ast.Gt())
                elif isinstance(op, ast.Gt):
                    new_ops.append(ast.Lt())
                elif isinstance(op, ast.Eq):
                    new_ops.append(ast.NotEq())
                elif isinstance(op, ast.NotEq):
                    new_ops.append(ast.Eq())
                elif isinstance(op, ast.GtE):
                    new_ops.append(ast.LtE())
                elif isinstance(op, ast.LtE):
                    new_ops.append(ast.GtE())
                else:
                    new_ops.append(op)
                self.applied = True
            else:
                new_ops.append(op)
            self.current_mutation_idx += 1
        node.ops = new_ops
        return node

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)
        if self.current_mutation_idx == self.target_mutation_id and not self.applied:
            if isinstance(node.op, ast.Add):
                node.op = ast.Sub()
                self.applied = True
            elif isinstance(node.op, ast.Sub):
                node.op = ast.Add()
                self.applied = True
            elif isinstance(node.op, ast.Mult):
                node.op = ast.FloorDiv()
                self.applied = True
        self.current_mutation_idx += 1
        return node


class MutationTestingEngine:
    """Calculates mutation score by generating mutants and evaluating if test suites kill them."""
    @staticmethod
    def count_mutation_points(source_code: str) -> int:
        tree = ast.parse(source_code)
        count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                count += len(node.ops)
            elif isinstance(node, ast.BinOp):
                if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
                    count += 1
        return count

    @staticmethod
    def generate_mutant_code(source_code: str, mutation_id: int) -> str:
        tree = ast.parse(source_code)
        visitor = MutationVisitor(mutation_id)
        mutated_tree = visitor.visit(tree)
        ast.fix_missing_locations(mutated_tree)
        return ast.unparse(mutated_tree)

    @staticmethod
    def evaluate_mutation_score(source_code: str, test_suite: Callable[[Dict[str, Any]], bool]) -> Dict[str, Any]:
        """
        Executes test_suite against original and all mutants.
        test_suite receives the namespace dict containing compiled functions.
        Returns kill ratio and mutation score percentage.
        """
        total_points = MutationTestingEngine.count_mutation_points(source_code)
        mutants_killed = 0
        mutants_survived = 0
        
        for mid in range(total_points):
            mutant_src = MutationTestingEngine.generate_mutant_code(source_code, mid)
            mutant_namespace: Dict[str, Any] = {}
            try:
                exec(mutant_src, mutant_namespace)
                # Run the test suite against mutant
                test_passed = test_suite(mutant_namespace)
                if test_passed:
                    # Test passed against a buggy mutant -> mutant SURVIVED (test suite weak)
                    mutants_survived += 1
                else:
                    # Test failed -> mutant KILLED (good test suite)
                    mutants_killed += 1
            except Exception:
                # Any exception or assertion error in test execution means mutant was KILLED
                mutants_killed += 1

        score_pct = (mutants_killed / total_points * 100.0) if total_points > 0 else 100.0
        return {
            "total_mutants": total_points,
            "killed": mutants_killed,
            "survived": mutants_survived,
            "mutation_score_pct": score_pct
        }


# ============================================================================
# Section 3: Consumer-Driven Contract Validator
# ============================================================================

class ContractValidator:
    """Validates HTTP API payloads against consumer pact schema expectations."""
    @staticmethod
    def validate_schema(payload: Dict[str, Any], schema: Dict[str, type]) -> Tuple[bool, List[str]]:
        errors = []
        for field, expected_type in schema.items():
            if field not in payload:
                errors.append(f"Missing required field '{field}'")
            elif not isinstance(payload[field], expected_type):
                actual_type = type(payload[field]).__name__
                errors.append(f"Field '{field}' expected type {expected_type.__name__}, got {actual_type}")
        return len(errors) == 0, errors


# ============================================================================
# Section 4: Automated Verification Test Suite
# ============================================================================

def run_tests():
    print("=== Level 5 Chapter 9: Testing at Scale Lab ===")

    # Test 1: Dummy & Stub
    dummy = DummyLogger()
    stub_fx = StubExchangeRateService(fixed_rate=83.5)
    assert stub_fx.get_rate("USD", "INR") == 83.5

    # Test 2: Spy
    spy = SpyNotificationService()
    spy.send_sms("+919876543210", "OTP: 4892")
    assert spy.call_count == 1
    assert spy.was_called_with("+919876543210", "OTP: 4892")
    assert not spy.was_called_with("+919876543210", "OTHER")
    print("  [PASS] Dummy, Stub, and Spy Doubles Validated")

    # Test 3: Mock Expectations
    mock = MockPaymentGateway()
    mock.expect("charge", "user_101", 49.99)
    mock.charge("user_101", 49.99)
    assert mock.verify() is True
    
    mock_bad = MockPaymentGateway()
    mock_bad.expect("charge", "user_101", 100.0)
    mock_bad.charge("user_101", 20.0)
    try:
        mock_bad.verify()
        assert False, "Should fail verification"
    except AssertionError as e:
        assert "Mock verification failed" in str(e)
    print("  [PASS] Mock Object Pre-programmed Expectations Verified")

    # Test 4: Fake Database Repository
    fake_db = FakeDatabaseRepository()
    fake_db.save("prod_42", {"name": "Mechanical Keyboard", "price": 99.0})
    rec = fake_db.find_by_id("prod_42")
    assert rec["name"] == "Mechanical Keyboard"
    assert fake_db.delete("prod_42") is True
    assert fake_db.find_by_id("prod_42") is None
    print("  [PASS] Fake In-Memory Database Double Validated")

    # Test 5: Mutation Testing Engine
    source_to_test = """
def calculate_discount(price, is_vip):
    if price > 100:
        base = price - 10
    else:
        base = price
    if is_vip:
        return base - 5
    return base
"""
    # Robust test suite that kills mutants
    def comprehensive_test_suite(env: Dict[str, Any]) -> bool:
        fn = env["calculate_discount"]
        try:
            assert fn(150, False) == 140
            assert fn(50, False) == 50
            assert fn(150, True) == 135
            assert fn(50, True) == 45
            return True
        except (AssertionError, TypeError, KeyError):
            return False

    report = MutationTestingEngine.evaluate_mutation_score(source_to_test, comprehensive_test_suite)
    assert report["total_mutants"] > 0
    assert report["killed"] == report["total_mutants"], f"Expected 100% mutation score, got {report}"
    assert report["mutation_score_pct"] == 100.0
    print(f"  [PASS] Mutation Testing Engine: {report['killed']}/{report['total_mutants']} mutants killed (Score: 100.0%)")

    # Test 6: Contract Schema Validator
    schema = {"order_id": str, "total_cents": int, "is_paid": bool}
    valid_payload = {"order_id": "ord_9901", "total_cents": 4500, "is_paid": True}
    invalid_payload = {"order_id": "ord_9901", "total_cents": "45.00", "is_paid": True}
    
    ok1, errs1 = ContractValidator.validate_schema(valid_payload, schema)
    assert ok1 is True and len(errs1) == 0
    
    ok2, errs2 = ContractValidator.validate_schema(invalid_payload, schema)
    assert ok2 is False and len(errs2) == 1
    assert "total_cents" in errs2[0]
    print("  [PASS] Consumer-Driven Contract Validator Schema Testing Validated")

    print("ALL TESTS PASSED: Level 5 Chapter 9 Testing at Scale Engine verified successfully.")


if __name__ == "__main__":
    run_tests()
