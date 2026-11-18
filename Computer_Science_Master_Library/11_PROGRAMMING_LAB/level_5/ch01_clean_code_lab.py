"""
Level 5 Chapter 01 Programming Lab: Clean Code, SOLID Principles & Refactoring
=============================================================================
Focus: Refactoring a tightly coupled procedural monolith into a modular,
       100% testable architecture adhering to all five SOLID principles,
       verifying Design by Contract invariants and Cyclomatic Complexity.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# 1. Monolithic Procedural Anti-Pattern (Before Refactoring)
# ---------------------------------------------------------------------------

class LegacyPaymentProcessor:
    """Violates SRP, OCP, DIP, and has high Cyclomatic Complexity."""
    def process_transaction(self, user_id: str, amount: float, method: str, target: str) -> bool:
        # High cyclomatic complexity with nested conditionals and mixed responsibilities
        if amount <= 0:
            return False
        
        # Mixed DB lookup, payment gateway logic, and notification logic
        print(f"[LEGACY] Fetching user {user_id} directly from hardcoded DB...")
        
        if method == "CREDIT_CARD":
            if not target.startswith("4") and not target.startswith("5"):
                return False
            print(f"[LEGACY] Charging Credit Card {target} for ${amount:.2f}")
        elif method == "UPI":
            if "@" not in target:
                return False
            print(f"[LEGACY] Transferring via UPI {target} for ${amount:.2f}")
        elif method == "CRYPTO":
            if len(target) < 10:
                return False
            print(f"[LEGACY] Transferring Crypto to {target} for ${amount:.2f}")
        else:
            return False

        # Direct hardcoded email dispatch
        print(f"[LEGACY] Sending hardcoded SMTP email to user_{user_id}@example.com")
        return True


# ---------------------------------------------------------------------------
# 2. Clean Architecture & SOLID Refactored Design (After Refactoring)
# ---------------------------------------------------------------------------

# [DIP & ISP]: Fine-grained abstractions
class IPaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: float, destination: str) -> bool:
        pass


class INotificationService(ABC):
    @abstractmethod
    def send_receipt(self, recipient: str, amount: float, status: str) -> None:
        pass


class IUserRepository(ABC):
    @abstractmethod
    def get_email_by_id(self, user_id: str) -> Optional[str]:
        pass


# [OCP]: New payment gateways are added by extension, without modifying existing code
class CreditCardGateway(IPaymentGateway):
    def charge(self, amount: float, destination: str) -> bool:
        if amount <= 0 or (not destination.startswith("4") and not destination.startswith("5")):
            return False
        return True


class UpiGateway(IPaymentGateway):
    def charge(self, amount: float, destination: str) -> bool:
        if amount <= 0 or "@" not in destination:
            return False
        return True


class CryptoGateway(IPaymentGateway):
    def charge(self, amount: float, destination: str) -> bool:
        if amount <= 0 or len(destination) < 10:
            return False
        return True


# [SRP]: Single Responsibility - In-memory user store
class InMemoryUserRepository(IUserRepository):
    def __init__(self, users: Dict[str, str]):
        self._users = users

    def get_email_by_id(self, user_id: str) -> Optional[str]:
        return self._users.get(user_id)


# [SRP]: Single Responsibility - Notification service
class MockNotificationService(INotificationService):
    def __init__(self):
        self.sent_receipts: List[Tuple[str, float, str]] = []

    def send_receipt(self, recipient: str, amount: float, status: str) -> None:
        self.sent_receipts.append((recipient, amount, status))


# [DIP & SRP]: High-level domain service depending strictly on abstractions
class PaymentService:
    def __init__(
        self,
        user_repo: IUserRepository,
        notification_service: INotificationService,
        gateways: Dict[str, IPaymentGateway]
    ):
        self._user_repo = user_repo
        self._notifier = notification_service
        self._gateways = gateways

    def process_payment(self, user_id: str, amount: float, method: str, destination: str) -> bool:
        # Precondition check (Design by Contract)
        if amount <= 0:
            raise ValueError("Payment amount must be positive.")

        email = self._user_repo.get_email_by_id(user_id)
        if not email:
            raise KeyError(f"User {user_id} not found.")

        gateway = self._gateways.get(method)
        if not gateway:
            raise ValueError(f"Unsupported payment method: {method}")

        # Polymorphic dispatch
        success = gateway.charge(amount, destination)
        status_str = "SUCCESS" if success else "FAILED"

        self._notifier.send_receipt(email, amount, status_str)
        return success


# ---------------------------------------------------------------------------
# 3. Liskov Substitution Principle (LSP) Verification
# ---------------------------------------------------------------------------

class Rectangle:
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    def set_width(self, width: float):
        self._width = width

    def set_height(self, height: float):
        self._height = height

    def area(self) -> float:
        return self._width * self._height


class Square(Rectangle):
    """Violates LSP if mutating width changes height unexpectedly."""
    def set_width(self, width: float):
        self._width = width
        self._height = width

    def set_height(self, height: float):
        self._width = height
        self._height = height


def check_lsp_compliance(rect: Rectangle) -> bool:
    """Verifies invariant: setting width then height produces width * height area."""
    rect.set_width(5.0)
    rect.set_height(4.0)
    return rect.area() == 20.0


def test_clean_code_suite():
    print("[TEST 1] Testing Monolithic Legacy Implementation...")
    legacy = LegacyPaymentProcessor()
    res1 = legacy.process_transaction("U1", 100.0, "CREDIT_CARD", "4111222233334444")
    assert res1 is True, "Legacy processor failed on valid card"
    print("  -> Legacy monolith executed with tight coupling.")

    print("[TEST 2] Testing Refactored SOLID Architecture...")
    user_db = {"U101": "alice@antigravity.dev", "U102": "bob@antigravity.dev"}
    repo = InMemoryUserRepository(user_db)
    notifier = MockNotificationService()
    gateways = {
        "CREDIT_CARD": CreditCardGateway(),
        "UPI": UpiGateway(),
        "CRYPTO": CryptoGateway(),
    }

    service = PaymentService(repo, notifier, gateways)

    # Valid UPI transaction
    success = service.process_payment("U101", 2500.0, "UPI", "alice@okhdfcbank")
    assert success is True, "SOLID payment service failed on valid UPI payment"
    assert len(notifier.sent_receipts) == 1, "Notification not dispatched"
    assert notifier.sent_receipts[0] == ("alice@antigravity.dev", 2500.0, "SUCCESS")
    print("  -> Clean architecture successfully processed payment with zero coupling.")

    # Extension test (Open/Closed): Add a new LoyaltyPointsGateway without modifying PaymentService!
    class LoyaltyPointsGateway(IPaymentGateway):
        def charge(self, amount: float, destination: str) -> bool:
            return destination.startswith("POINTS_")

    gateways["LOYALTY"] = LoyaltyPointsGateway()
    points_success = service.process_payment("U102", 50.0, "LOYALTY", "POINTS_9981")
    assert points_success is True, "OCP extension failed"
    print("  -> Open/Closed Principle verified: Added LoyaltyPointsGateway with 0 modifications to PaymentService.")

    print("[TEST 3] Liskov Substitution Principle (LSP) Verification...")
    r = Rectangle(2.0, 3.0)
    assert check_lsp_compliance(r) is True, "Standard Rectangle should satisfy contract"

    sq = Square(2.0, 2.0)
    assert check_lsp_compliance(sq) is False, "Square should fail LSP rectangle contract (proving violation)"
    print("  -> LSP violation mathematically trapped: Subtype failed supertype contract.")

    print("ALL Level 5 Chapter 01 Clean Code lab tests passed successfully!")


if __name__ == "__main__":
    test_clean_code_suite()
