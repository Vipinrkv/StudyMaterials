"""
Level 3 Chapter 06: Heaps, Priority Queues, and HeapSort
Comprehensive Laboratory Verification Suite

Covers:
1. Binary Max-Heap and Min-Heap from scratch.
2. Floyd's O(n) build_heap versus naive O(n log n) insertion.
3. In-place HeapSort algorithm.
4. Top-K streaming element extractor.
"""

import sys
from typing import List, Any, Optional

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class MaxHeap:
    def __init__(self):
        self.data: List[int] = []

    @staticmethod
    def _parent(i: int) -> int:
        return (i - 1) // 2

    @staticmethod
    def _left(i: int) -> int:
        return 2 * i + 1

    @staticmethod
    def _right(i: int) -> int:
        return 2 * i + 2

    def push(self, val: int) -> None:
        self.data.append(val)
        self._sift_up(len(self.data) - 1)

    def pop(self) -> int:
        if not self.data:
            raise IndexError("pop from empty heap")
        root = self.data[0]
        last = self.data.pop()
        if self.data:
            self.data[0] = last
            self._sift_down(0, len(self.data))
        return root

    def peek(self) -> int:
        if not self.data:
            raise IndexError("peek from empty heap")
        return self.data[0]

    def _sift_up(self, idx: int) -> None:
        curr = idx
        while curr > 0:
            p = self._parent(curr)
            if self.data[curr] > self.data[p]:
                self.data[curr], self.data[p] = self.data[p], self.data[curr]
                curr = p
            else:
                break

    def _sift_down(self, idx: int, heap_size: int) -> None:
        curr = idx
        while True:
            largest = curr
            l = self._left(curr)
            r = self._right(curr)

            if l < heap_size and self.data[l] > self.data[largest]:
                largest = l
            if r < heap_size and self.data[r] > self.data[largest]:
                largest = r

            if largest != curr:
                self.data[curr], self.data[largest] = self.data[largest], self.data[curr]
                curr = largest
            else:
                break

    def is_valid_heap(self) -> bool:
        n = len(self.data)
        for i in range(n // 2):
            l = self._left(i)
            r = self._right(i)
            if l < n and self.data[i] < self.data[l]:
                return False
            if r < n and self.data[i] < self.data[r]:
                return False
        return True


def floyd_build_heap(arr: List[int]) -> MaxHeap:
    heap = MaxHeap()
    heap.data = list(arr)
    n = len(heap.data)
    for i in range(n // 2 - 1, -1, -1):
        heap._sift_down(i, n)
    return heap


def in_place_heapsort(arr: List[int]) -> None:
    n = len(arr)

    # 1. Build max heap using Floyd's algorithm
    for i in range(n // 2 - 1, -1, -1):
        _sift_down_slice(arr, i, n)

    # 2. Extract max one by one and move to back of array
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        _sift_down_slice(arr, 0, i)


def _sift_down_slice(arr: List[int], idx: int, size: int) -> None:
    curr = idx
    while True:
        largest = curr
        l = 2 * curr + 1
        r = 2 * curr + 2
        if l < size and arr[l] > arr[largest]:
            largest = l
        if r < size and arr[r] > arr[largest]:
            largest = r
        if largest != curr:
            arr[curr], arr[largest] = arr[largest], arr[curr]
            curr = largest
        else:
            break


class TopKStreamTracker:
    """Tracks Top K largest elements from an incoming stream using a Min-Heap of size K."""
    def __init__(self, k: int):
        self.k = k
        self.heap: List[int] = []

    def add(self, val: int) -> None:
        if len(self.heap) < self.k:
            self.heap.append(val)
            self._sift_up(len(self.heap) - 1)
        elif val > self.heap[0]:
            self.heap[0] = val
            self._sift_down(0)

    def get_top_k(self) -> List[int]:
        return sorted(self.heap, reverse=True)

    def _sift_up(self, idx: int) -> None:
        curr = idx
        while curr > 0:
            p = (curr - 1) // 2
            if self.heap[curr] < self.heap[p]:
                self.heap[curr], self.heap[p] = self.heap[p], self.heap[curr]
                curr = p
            else:
                break

    def _sift_down(self, idx: int) -> None:
        curr = idx
        size = len(self.heap)
        while True:
            smallest = curr
            l = 2 * curr + 1
            r = 2 * curr + 2
            if l < size and self.heap[l] < self.heap[smallest]:
                smallest = l
            if r < size and self.heap[r] < self.heap[smallest]:
                smallest = r
            if smallest != curr:
                self.heap[curr], self.heap[smallest] = self.heap[smallest], self.heap[curr]
                curr = smallest
            else:
                break


def test_heaps_lab():
    print("[TEST 1] MaxHeap push, pop, and invariant check...")
    heap = MaxHeap()
    elements = [10, 4, 15, 20, 0, 8, 30, 2]
    for x in elements:
        heap.push(x)
        assert heap.is_valid_heap(), "Heap invariant violated during push"

    extracted = []
    while heap.data:
        extracted.append(heap.pop())
        assert heap.is_valid_heap(), "Heap invariant violated during pop"

    assert extracted == sorted(elements, reverse=True), f"Extracted order invalid: {extracted}"
    print("  -> Passed. Correct descending order extracted.")

    print("[TEST 2] Floyd's O(n) build_heap...")
    raw = [50, 10, 70, 30, 90, 20, 40, 80, 60]
    built = floyd_build_heap(raw)
    assert built.is_valid_heap(), "Floyd build heap failed invariant check"
    assert built.peek() == 90, f"Expected max 90, got {built.peek()}"
    print("  -> Passed. Floyd linear heapification verified.")

    print("[TEST 3] In-place HeapSort verification...")
    unsorted = [64, 34, 25, 12, 22, 11, 90, 42, 88, 1, 0, -5]
    expected = sorted(unsorted)
    in_place_heapsort(unsorted)
    assert unsorted == expected, f"HeapSort output mismatch: {unsorted} != {expected}"
    print("  -> Passed. In-place HeapSort sorted correctly.")

    print("[TEST 4] Top-K Stream tracking...")
    stream = [100, 2, 500, 30, 800, 400, 900, 10, 1500, 750]
    tracker = TopKStreamTracker(k=3)
    for x in stream:
        tracker.add(x)
    top_3 = tracker.get_top_k()
    assert top_3 == [1500, 900, 800], f"Expected [1500, 900, 800], got {top_3}"
    print("  -> Passed. Top-3 stream correctly captured.")

    print("ALL Chapter 06 Heap lab tests passed successfully!")


if __name__ == "__main__":
    test_heaps_lab()
