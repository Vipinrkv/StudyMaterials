"""
Level 5 Chapter 03 Programming Lab: Behavioral & Enterprise Design Patterns
==========================================================================
Focus: Strategy Pattern, Observer Pattern (EventBus), State Pattern (Order FSM),
       and Repository + Unit of Work with dirty tracking and atomic commit.
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
from typing import Dict, List, Set, Callable, Optional, Any
from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# 1. Behavioral: Strategy Pattern (Dynamic Pricing)
# ---------------------------------------------------------------------------

class IPricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, base_price: float, items_count: int) -> float:
        pass


class RegularPricingStrategy(IPricingStrategy):
    def calculate_price(self, base_price: float, items_count: int) -> float:
        return base_price * items_count


class SurgePricingStrategy(IPricingStrategy):
    def __init__(self, multiplier: float = 1.5):
        self.multiplier = multiplier

    def calculate_price(self, base_price: float, items_count: int) -> float:
        return (base_price * items_count) * self.multiplier


class VipDiscountPricingStrategy(IPricingStrategy):
    def calculate_price(self, base_price: float, items_count: int) -> float:
        raw = base_price * items_count
        return raw * 0.80  # 20% discount


# ---------------------------------------------------------------------------
# 2. Behavioral: Observer Pattern (EventBus)
# ---------------------------------------------------------------------------

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Any], None]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, event_type: str, data: Any):
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                handler(data)


# ---------------------------------------------------------------------------
# 3. Behavioral: State Pattern (Order Finite State Machine)
# ---------------------------------------------------------------------------

class OrderState(ABC):
    @abstractmethod
    def submit_payment(self, context: 'OrderContext') -> str:
        pass

    @abstractmethod
    def ship_order(self, context: 'OrderContext') -> str:
        pass

    @abstractmethod
    def deliver_order(self, context: 'OrderContext') -> str:
        pass


class DraftState(OrderState):
    def submit_payment(self, context: 'OrderContext') -> str:
        context.set_state(PaidState())
        return "Payment processed successfully. Transitioned to PaidState."

    def ship_order(self, context: 'OrderContext') -> str:
        raise ValueError("Cannot ship an unpaid draft order!")

    def deliver_order(self, context: 'OrderContext') -> str:
        raise ValueError("Cannot deliver an unpaid draft order!")


class PaidState(OrderState):
    def submit_payment(self, context: 'OrderContext') -> str:
        raise ValueError("Order is already paid!")

    def ship_order(self, context: 'OrderContext') -> str:
        context.set_state(ShippedState())
        return "Order has been dispatched. Transitioned to ShippedState."

    def deliver_order(self, context: 'OrderContext') -> str:
        raise ValueError("Cannot deliver an unshipped order!")


class ShippedState(OrderState):
    def submit_payment(self, context: 'OrderContext') -> str:
        raise ValueError("Order is already paid and in transit!")

    def ship_order(self, context: 'OrderContext') -> str:
        raise ValueError("Order is already shipped!")

    def deliver_order(self, context: 'OrderContext') -> str:
        context.set_state(DeliveredState())
        return "Order handed over to customer. Transitioned to DeliveredState."


class DeliveredState(OrderState):
    def submit_payment(self, context: 'OrderContext') -> str:
        raise ValueError("Order already completed.")

    def ship_order(self, context: 'OrderContext') -> str:
        raise ValueError("Order already completed.")

    def deliver_order(self, context: 'OrderContext') -> str:
        raise ValueError("Order already delivered.")


class OrderContext:
    def __init__(self, order_id: str):
        self.order_id = order_id
        self._state: OrderState = DraftState()

    def set_state(self, state: OrderState):
        self._state = state

    @property
    def current_state_name(self) -> str:
        return self._state.__class__.__name__

    def pay(self) -> str:
        return self._state.submit_payment(self)

    def ship(self) -> str:
        return self._state.ship_order(self)

    def deliver(self) -> str:
        return self._state.deliver_order(self)


# ---------------------------------------------------------------------------
# 4. Enterprise: Unit of Work & Repository Pattern
# ---------------------------------------------------------------------------

class UserEntity:
    def __init__(self, user_id: str, name: str, balance: float):
        self.user_id = user_id
        self.name = name
        self.balance = balance

    def __repr__(self):
        return f"User({self.user_id}, {self.name}, ${self.balance:.2f})"


class IUserRepository(ABC):
    @abstractmethod
    def get(self, user_id: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def add(self, user: UserEntity) -> None:
        pass


class UnitOfWork:
    def __init__(self, persistent_storage: Dict[str, UserEntity]):
        self._storage = persistent_storage
        self.new_entities: Dict[str, UserEntity] = {}
        self.dirty_entities: Dict[str, UserEntity] = {}
        self.identity_map: Dict[str, UserEntity] = {}

    def get_user(self, user_id: str) -> Optional[UserEntity]:
        # Identity Map: return cached instance if already loaded
        if user_id in self.identity_map:
            return self.identity_map[user_id]
        if user_id in self._storage:
            # Clone entity to track changes
            persisted = self._storage[user_id]
            user = UserEntity(persisted.user_id, persisted.name, persisted.balance)
            self.identity_map[user_id] = user
            return user
        return None

    def register_new(self, user: UserEntity):
        self.new_entities[user.user_id] = user
        self.identity_map[user.user_id] = user

    def register_dirty(self, user: UserEntity):
        self.dirty_entities[user.user_id] = user

    def commit(self):
        # Atomic batch flush
        for u_id, entity in self.new_entities.items():
            self._storage[u_id] = entity
        for u_id, entity in self.dirty_entities.items():
            self._storage[u_id] = entity
        self.new_entities.clear()
        self.dirty_entities.clear()

    def rollback(self):
        self.new_entities.clear()
        self.dirty_entities.clear()
        self.identity_map.clear()


def test_behavioral_suite():
    print("[TEST 1] Strategy Pattern (Dynamic Pricing Engine)...")
    base = 100.0
    items = 3

    reg_strat = RegularPricingStrategy()
    surge_strat = SurgePricingStrategy(multiplier=1.8)
    vip_strat = VipDiscountPricingStrategy()

    assert reg_strat.calculate_price(base, items) == 300.0, "Regular pricing mismatch"
    assert surge_strat.calculate_price(base, items) == 540.0, "Surge pricing mismatch"
    assert vip_strat.calculate_price(base, items) == 240.0, "VIP pricing mismatch"
    print("  -> Regular: $300.00, Surge(1.8x): $540.00, VIP(20% off): $240.00 (All verified).")

    print("[TEST 2] Observer Pattern (EventBus Dispatcher)...")
    bus = EventBus()
    received_events = []

    def email_handler(data): received_events.append(f"EMAIL:{data['id']}")
    def audit_handler(data): received_events.append(f"AUDIT:{data['id']}")

    bus.subscribe("ORDER_PLACED", email_handler)
    bus.subscribe("ORDER_PLACED", audit_handler)
    bus.publish("ORDER_PLACED", {"id": "ORD-90210"})

    assert len(received_events) == 2
    assert "EMAIL:ORD-90210" in received_events and "AUDIT:ORD-90210" in received_events
    print(f"  -> Dispatched 1 event to 2 independent subscribers: {received_events}")

    print("[TEST 3] State Pattern (Finite State Machine Transitions)...")
    order = OrderContext("ORD-101")
    assert order.current_state_name == "DraftState"

    msg1 = order.pay()
    assert order.current_state_name == "PaidState"

    msg2 = order.ship()
    assert order.current_state_name == "ShippedState"

    msg3 = order.deliver()
    assert order.current_state_name == "DeliveredState"

    # Verify invalid state transition rejection
    try:
        order.ship()  # Cannot ship an already delivered order
        assert False, "Should have thrown ValueError for illegal transition"
    except ValueError as e:
        print(f"  -> Successfully caught illegal state transition: '{e}'")

    print("[TEST 4] Enterprise Unit of Work & Identity Map...")
    db_table: Dict[str, UserEntity] = {
        "USR-1": UserEntity("USR-1", "Alice", 500.0),
        "USR-2": UserEntity("USR-2", "Bob", 1200.0)
    }

    uow = UnitOfWork(db_table)
    # 1. Fetch user (tests Identity Map)
    u1 = uow.get_user("USR-1")
    u1_again = uow.get_user("USR-1")
    assert u1 is u1_again, "Identity Map failed to return identical in-memory instance!"

    # 2. Modify balance and register dirty
    u1.balance += 250.0
    uow.register_dirty(u1)

    # 3. Register new user
    new_user = UserEntity("USR-3", "Charlie", 350.0)
    uow.register_new(new_user)

    # Before commit, db_table should be unchanged
    assert db_table["USR-1"].balance == 500.0
    assert "USR-3" not in db_table

    # Commit changes
    uow.commit()
    assert db_table["USR-1"].balance == 750.0
    assert db_table["USR-3"].balance == 350.0
    print("  -> Unit of Work successfully batched and atomically committed entity updates.")

    print("ALL Level 5 Chapter 03 Behavioral & Enterprise lab tests passed successfully!")


if __name__ == "__main__":
    test_behavioral_suite()
