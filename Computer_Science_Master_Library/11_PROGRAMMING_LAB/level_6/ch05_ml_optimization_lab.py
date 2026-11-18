# -*- coding: utf-8 -*-
"""
CH05: Machine Learning Mathematical Foundations and Optimization Lab
====================================================================
Covers:
1. Analytical vs Numerical Gradient Checker (Central Difference Formula).
2. Pure-Python Optimizers: Plain SGD, Momentum, Adam, and AdamW.
3. Convergence Benchmark on Non-Convex Rosenbrock Banana Function.
"""
import sys
import math
from typing import Callable, Dict, List, Tuple

sys.stdout.reconfigure(encoding="utf-8")


# ============================================================================
# Section 1: Vector Operations & Numerical Gradient Checker
# ============================================================================

def vector_l2_norm(v: List[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def compute_numerical_gradient(func: Callable[[List[float]], float], theta: List[float], epsilon: float = 1e-6) -> List[float]:
    """Computes two-sided central difference numerical gradient."""
    grad = []
    for i in range(len(theta)):
        theta_plus = list(theta)
        theta_minus = list(theta)
        theta_plus[i] += epsilon
        theta_minus[i] -= epsilon
        
        f_plus = func(theta_plus)
        f_minus = func(theta_minus)
        grad.append((f_plus - f_minus) / (2.0 * epsilon))
    return grad


def check_gradient_error(analytical_grad: List[float], numerical_grad: List[float]) -> float:
    """
    Computes normalized relative error:
    ||g_analytical - g_numerical|| / (||g_analytical|| + ||g_numerical|| + 1e-12)
    """
    diff_vector = [a - n for a, n in zip(analytical_grad, numerical_grad)]
    numerator = vector_l2_norm(diff_vector)
    denominator = vector_l2_norm(analytical_grad) + vector_l2_norm(numerical_grad) + 1e-12
    return numerator / denominator


# ============================================================================
# Section 2: Non-Convex Benchmark: Rosenbrock Banana Function
# ============================================================================

def rosenbrock(theta: List[float], a: float = 1.0, b: float = 100.0) -> float:
    """f(x, y) = (a - x)^2 + b * (y - x^2)^2. Global minimum at (a, a^2) = (1, 1)."""
    x, y = theta[0], theta[1]
    return (a - x) ** 2 + b * (y - x ** 2) ** 2


def rosenbrock_grad(theta: List[float], a: float = 1.0, b: float = 100.0) -> List[float]:
    """Analytical gradient of Rosenbrock function."""
    x, y = theta[0], theta[1]
    df_dx = -2.0 * (a - x) - 4.0 * b * x * (y - x ** 2)
    df_dy = 2.0 * b * (y - x ** 2)
    return [df_dx, df_dy]


# ============================================================================
# Section 3: Pure-Python First-Order Optimizers
# ============================================================================

class SGDMomentum:
    """Stochastic Gradient Descent with Classical Momentum."""
    def __init__(self, lr: float = 0.001, momentum: float = 0.9):
        self.lr = lr
        self.momentum = momentum
        self.velocity: Optional[List[float]] = None

    def step(self, theta: List[float], grad: List[float]) -> List[float]:
        if self.velocity is None:
            self.velocity = [0.0] * len(theta)
            
        for i in range(len(theta)):
            self.velocity[i] = self.momentum * self.velocity[i] + self.lr * grad[i]
            theta[i] -= self.velocity[i]
        return theta


class AdamW:
    """
    Adam with Decoupled Weight Decay (Loshchilov & Hutter 2017).
    Standard optimizer for modern foundation models (Transformers).
    """
    def __init__(self, lr: float = 0.01, beta1: float = 0.9, beta2: float = 0.999, eps: float = 1e-8, weight_decay: float = 0.01):
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.eps = eps
        self.weight_decay = weight_decay
        
        self.m: Optional[List[float]] = None  # First moment vector
        self.v: Optional[List[float]] = None  # Second moment vector
        self.t = 0                           # Time step

    def step(self, theta: List[float], grad: List[float]) -> List[float]:
        if self.m is None:
            self.m = [0.0] * len(theta)
            self.v = [0.0] * len(theta)
            
        self.t += 1
        
        for i in range(len(theta)):
            g = grad[i]
            # Update biased 1st moment: m_t = beta1 * m_{t-1} + (1 - beta1) * g
            self.m[i] = self.beta1 * self.m[i] + (1.0 - self.beta1) * g
            # Update biased 2nd moment: v_t = beta2 * v_{t-1} + (1 - beta2) * g^2
            self.v[i] = self.beta2 * self.v[i] + (1.0 - self.beta2) * (g * g)
            
            # Bias-corrected moments
            m_hat = self.m[i] / (1.0 - (self.beta1 ** self.t))
            v_hat = self.v[i] / (1.0 - (self.beta2 ** self.t))
            
            # Decoupled weight decay update:
            # theta_{t+1} = theta_t - lr * weight_decay * theta_t - (lr / (sqrt(v_hat) + eps)) * m_hat
            theta[i] = theta[i] - (self.lr * self.weight_decay * theta[i]) - (self.lr / (math.sqrt(v_hat) + self.eps)) * m_hat
            
        return theta


# ============================================================================
# Section 4: Automated Verification Test Suite
# ============================================================================

def run_tests():
    print("=== Level 6 Chapter 5: ML Mathematical Foundations & Optimization Lab ===")

    # Test 1: Gradient Checking on Non-Trivial Point
    test_theta = [1.2, 2.5]
    analytical_g = rosenbrock_grad(test_theta)
    numerical_g = compute_numerical_gradient(rosenbrock, test_theta, epsilon=1e-6)
    
    rel_error = check_gradient_error(analytical_g, numerical_g)
    assert rel_error < 1e-6, f"Gradient checking failed! Relative error {rel_error} exceeds 1e-6"
    print(f"  [PASS] Numerical Gradient Checking Validated (Relative Error: {rel_error:.2e} < 1e-6)")

    # Test 2: Adam Bias-Correction Verification
    # At t=1, m_1 = 0.1 * g, but m_hat_1 = (0.1 * g) / (1 - 0.9) = g! (Unbiased)
    adam_test = AdamW(lr=0.01, beta1=0.9, beta2=0.999, weight_decay=0.0)
    theta_dummy = [5.0]
    g_dummy = [10.0]
    adam_test.step(theta_dummy, g_dummy)
    
    # Assert that bias-corrected moment m_hat equals raw gradient 10.0
    m_hat_1 = adam_test.m[0] / (1.0 - (0.9 ** 1))
    assert abs(m_hat_1 - 10.0) < 1e-9
    print("  [PASS] Adam Bias-Correction Invariant Verified (t=1 m_hat == g)")

    # Test 3: Optimization Benchmark on Rosenbrock Valley
    # Start far from optimum: (-1.0, 1.0), Loss = (1 - (-1))^2 + 100*(1 - 1)^2 = 4.0
    theta_opt = [-1.0, 1.0]
    initial_loss = rosenbrock(theta_opt)
    assert initial_loss == 4.0

    optimizer = AdamW(lr=0.05, beta1=0.9, beta2=0.999, weight_decay=0.0)
    
    # Run 1000 steps of AdamW
    for step in range(1000):
        grad = rosenbrock_grad(theta_opt)
        theta_opt = optimizer.step(theta_opt, grad)

    final_loss = rosenbrock(theta_opt)
    
    # Verify convergence near global optimum (1.0, 1.0)
    assert final_loss < 0.05, f"Expected loss < 0.05, got {final_loss}"
    assert abs(theta_opt[0] - 1.0) < 0.15, f"x should be near 1.0, got {theta_opt[0]}"
    assert abs(theta_opt[1] - 1.0) < 0.15, f"y should be near 1.0, got {theta_opt[1]}"
    print(f"  [PASS] AdamW Converged on Non-Convex Valley: Loss dropped {initial_loss:.2f} -> {final_loss:.4f} "
          f"(Theta: [{theta_opt[0]:.3f}, {theta_opt[1]:.3f}])")

    print("ALL TESTS PASSED: Level 6 Chapter 5 ML Optimization Engine verified successfully.")


if __name__ == "__main__":
    run_tests()
