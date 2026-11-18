"""
ch06_deep_learning_autograd_lab.py
Level 6 Companion Lab: Reverse-Mode Automatic Differentiation & 2D Convolution Engine.
Pure Python/Standard Library implementation with zero external dependencies.
"""

from __future__ import annotations
import sys
import math
from typing import Set, Tuple, List, Union

# Windows UTF-8 console output
sys.stdout.reconfigure(encoding="utf-8")


class Value:
    """
    Scalar computational graph node supporting reverse-mode automatic differentiation.
    """
    def __init__(self, data: float, _children: Tuple[Value, ...] = (), _op: str = ""):
        self.data = float(data)
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = set(_children)
        self._op = _op

    def __repr__(self) -> str:
        return f"Value(data={self.data:.4f}, grad={self.grad:.4f})"

    def __add__(self, other: Union[Value, float]) -> Value:
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")

        def _backward():
            self.grad += 1.0 * out.grad
            other.grad += 1.0 * out.grad
        out._backward = _backward
        return out

    def __radd__(self, other: Union[Value, float]) -> Value:
        return self + other

    def __mul__(self, other: Union[Value, float]) -> Value:
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")

        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        out._backward = _backward
        return out

    def __rmul__(self, other: Union[Value, float]) -> Value:
        return self * other

    def __sub__(self, other: Union[Value, float]) -> Value:
        return self + (-other)

    def __rsub__(self, other: Union[Value, float]) -> Value:
        return Value(other) - self

    def __neg__(self) -> Value:
        return self * -1.0

    def relu(self) -> Value:
        out = Value(self.data if self.data > 0 else 0.0, (self,), "ReLU")

        def _backward():
            self.grad += (1.0 if self.data > 0 else 0.0) * out.grad
        out._backward = _backward
        return out

    def sigmoid(self) -> Value:
        # Numerically stable sigmoid
        s = 1.0 / (1.0 + math.exp(-max(-500.0, min(500.0, self.data))))
        out = Value(s, (self,), "Sigmoid")

        def _backward():
            self.grad += s * (1.0 - s) * out.grad
        out._backward = _backward
        return out

    def backward(self) -> None:
        """Topological sort followed by reverse-mode derivative propagation."""
        topo: List[Value] = []
        visited: Set[Value] = set()

        def build_topo(v: Value):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)

        build_topo(self)
        self.grad = 1.0
        for node in reversed(topo):
            node._backward()


def conv2d_forward(
    input_tensor: List[List[float]],
    kernel: List[List[float]],
    stride: int = 1,
    padding: int = 0
) -> List[List[float]]:
    """
    Computes 2D cross-correlation (convolution) over a single channel matrix.
    Formula: O = floor((H - K + 2P)/S) + 1
    """
    H = len(input_tensor)
    W = len(input_tensor[0])
    KH = len(kernel)
    KW = len(kernel[0])

    # Apply zero padding
    if padding > 0:
        padded_H = H + 2 * padding
        padded_W = W + 2 * padding
        padded = [[0.0 for _ in range(padded_W)] for _ in range(padded_H)]
        for r in range(H):
            for c in range(W):
                padded[r + padding][c + padding] = input_tensor[r][c]
    else:
        padded = input_tensor
        padded_H = H
        padded_W = W

    out_H = (padded_H - KH) // stride + 1
    out_W = (padded_W - KW) // stride + 1
    output = [[0.0 for _ in range(out_W)] for _ in range(out_H)]

    for r in range(out_H):
        for c in range(out_W):
            val = 0.0
            r_start = r * stride
            c_start = c * stride
            for kr in range(KH):
                for kc in range(KW):
                    val += padded[r_start + kr][c_start + kc] * kernel[kr][kc]
            output[r][c] = val

    return output


def test_autograd_scalar_derivatives():
    print("Running Test Suite 1: Scalar Autograd Derivative Verification...")
    # Function: f(x, y) = (x * y + 3) * (y - 2)
    # Let x = 2.0, y = 4.0
    # a = x * y = 8.0
    # b = a + 3 = 11.0
    # c = y - 2 = 2.0
    # f = b * c = 22.0
    # df/dx = df/db * db/da * da/dx = c * 1 * y = 2.0 * 4.0 = 8.0
    # df/dy = (da/dy * db/da * df/db) + (dc/dy * df/dc) = (x * 1 * c) + (1 * b) = (2 * 2) + 11 = 15.0
    x = Value(2.0)
    y = Value(4.0)
    f = (x * y + 3.0) * (y - 2.0)
    f.backward()

    assert abs(f.data - 22.0) < 1e-6, f"Expected f=22.0, got {f.data}"
    assert abs(x.grad - 8.0) < 1e-6, f"Expected df/dx=8.0, got {x.grad}"
    assert abs(y.grad - 15.0) < 1e-6, f"Expected df/dy=15.0, got {y.grad}"
    print(f"  Passed! f={f.data:.2f}, df/dx={x.grad:.2f}, df/dy={y.grad:.2f}")


def test_activation_backprop():
    print("Running Test Suite 2: Non-Linear Activation Backward Passes...")
    # Test ReLU
    v1 = Value(-3.5)
    out1 = v1.relu()
    out1.backward()
    assert abs(out1.data - 0.0) < 1e-6
    assert abs(v1.grad - 0.0) < 1e-6

    v2 = Value(4.2)
    out2 = v2.relu()
    out2.backward()
    assert abs(out2.data - 4.2) < 1e-6
    assert abs(v2.grad - 1.0) < 1e-6

    # Test Sigmoid
    v3 = Value(0.0)
    out3 = v3.sigmoid()
    out3.backward()
    # sigmoid(0) = 0.5; grad = 0.5 * (1 - 0.5) = 0.25
    assert abs(out3.data - 0.5) < 1e-6
    assert abs(v3.grad - 0.25) < 1e-6
    print(f"  Passed! ReLU & Sigmoid gradients match exact analytical values.")


def test_conv2d_engine():
    print("Running Test Suite 3: 2D Convolution Forward Pass Verification...")
    # 4x4 image
    img = [
        [1.0, 2.0, 3.0, 0.0],
        [0.0, 1.0, 2.0, 3.0],
        [3.0, 0.0, 1.0, 2.0],
        [2.0, 3.0, 0.0, 1.0]
    ]
    # 2x2 edge detection kernel
    kernel = [
        [1.0, -1.0],
        [1.0, -1.0]
    ]
    # Output size without padding: (4 - 2)/1 + 1 = 3x3
    out = conv2d_forward(img, kernel, stride=1, padding=0)
    assert len(out) == 3 and len(out[0]) == 3, f"Unexpected dimensions: {len(out)}x{len(out[0])}"

    # Top-left corner: (1 - 2) + (0 - 1) = -2.0
    assert abs(out[0][0] - (-2.0)) < 1e-6, f"Expected -2.0, got {out[0][0]}"

    # Output with padding = 1: (4 - 2 + 2)/1 + 1 = 5x5
    out_pad = conv2d_forward(img, kernel, stride=1, padding=1)
    assert len(out_pad) == 5 and len(out_pad[0]) == 5
    print(f"  Passed! Conv2D dimensions and convolution arithmetic verified.")


if __name__ == "__main__":
    print("================================================================================")
    print("LEVEL 6 LAB 06: DEEP LEARNING AUTOGRAD & CONVOLUTION ENGINE")
    print("================================================================================")
    test_autograd_scalar_derivatives()
    test_activation_backprop()
    test_conv2d_engine()
    print("================================================================================")
    print("ALL 3 TEST SUITES PASSED CLEANLY (EXIT CODE 0)")
    print("================================================================================")
