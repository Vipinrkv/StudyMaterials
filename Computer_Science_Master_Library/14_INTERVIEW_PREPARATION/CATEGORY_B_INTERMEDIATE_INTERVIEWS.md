# TECHNICAL INTERVIEW PREPARATION: CATEGORY B (INTERMEDIATE & SENIOR SDE)

**Target Roles:** SDE II, Senior Software Engineer, Backend Systems Engineer  
**Associated Library Levels:** Level 4 (Advanced Undergraduate), Level 5 (Professional Software Engineering), Level 6 (Postgraduate Advanced)  
**Teaching Principle:** "Teach Simply, Explain Deeply" — Concurrency hazards, database storage engines, and microservices resilience.

---

## 1. Interview Overview & Candidate Expectations
Senior SDE candidates are expected to demonstrate deep architectural fluency, concurrency mastery, and systems trade-off reasoning:
1. **Multi-Threaded Systems & Concurrency Hazards:** Race conditions, thread safety, lock-free primitives (CAS), and memory consistency models.
2. **Database Storage Internals:** B+ Trees vs. LSM Trees, ACID transaction anomalies, and indexing optimizations.
3. **Resilient Microservices Architecture:** Circuit breakers, token bucket rate limiting, idempotency keys, and Saga transactions.
4. **Algorithmic Depth:** Dynamic programming optimizations, graph traversals, and amortized complexity.

---

## 2. Concurrency, Locks & Memory Barriers

### Q1: Double-Checked Locking (DCL) & Hardware Memory Reordering
**Question:** Why is the naive implementation of Double-Checked Locking for Singletons broken in multithreaded environments without memory barriers?
```java
public class BrokenSingleton {
    private static BrokenSingleton instance;
    public static BrokenSingleton getInstance() {
        if (instance == null) {
            synchronized (BrokenSingleton.class) {
                if (instance == null) {
                    instance = new BrokenSingleton(); // FATAL DEFECT HERE
                }
            }
        }
        return instance;
    }
}
```

**Deep Explanation:**
The line `instance = new BrokenSingleton()` is not an atomic CPU operation. It expands into three distinct machine steps:
1. `mem = allocate(sizeof(BrokenSingleton));` // Allocate heap memory
2. `ctor(mem);`                               // Initialize fields inside constructor
3. `instance = mem;`                          // Publish reference to global pointer

Because the CPU and compiler are free to reorder instructions that have no internal data dependency, Step 3 may execute **before** Step 2 (`1 -> 3 -> 2` reordering).
If Thread A executes `1 -> 3` and is preempted before `2`:
- Thread B calls `getInstance()`.
- Thread B checks `if (instance == null)`. Since `instance` holds the non-null address `mem`, the check evaluates to `false`.
- Thread B returns `instance` and dereferences its fields *before the constructor finishes running*, resulting in memory corruption or uninitialized null reads!

**The Fix:**
Declare `instance` as `volatile` (in Java/C#) or use `std::atomic` with memory order acquire/release (in C++):
```java
private static volatile BrokenSingleton instance;
```
The `volatile` modifier introduces a hardware **Store-Store memory fence**, guaranteeing that all writes to the allocated object complete before the reference publication becomes globally visible to other CPU cores.

---

### Q2: Deadlock Necessary Conditions & Coffman Prevention
**Question:** State the four Coffman conditions necessary for a deadlock to occur. How can you mathematically prevent deadlocks in a high-concurrency banking system transferring money between two accounts?

**Deep Explanation:**
The four Coffman conditions are:
1. **Mutual Exclusion:** Resources cannot be shared simultaneously.
2. **Hold and Wait:** A process holding a resource requests additional resources.
3. **No Preemption:** Resources cannot be forcibly seized from a holding process.
4. **Circular Wait:** A closed chain of processes exists, where each holds a resource requested by the next.

**Deadlock in Account Transfer:**
```python
def transfer(from_acc, to_acc, amount):
    with from_acc.lock:
        with to_acc.lock:
            from_acc.balance -= amount
            to_acc.balance += amount
```
If Thread 1 transfers from Account A to B, and Thread 2 transfers from B to A concurrently, Thread 1 acquires lock A and waits for lock B, while Thread 2 acquires lock B and waits for lock A $\implies$ **Circular Wait Deadlock**.

**The Mathematical Solution: Global Lock Hierarchy (Breaking Condition 4):**
Impose a strict global total ordering on all resource identifiers (e.g., account IDs):
```python
def safe_transfer(acc1, acc2, amount):
    # Enforce total ordering: always acquire lower ID first
    first = acc1 if acc1.id < acc2.id else acc2
    second = acc2 if acc1.id < acc2.id else acc1

    with first.lock:
        with second.lock:
            acc1.balance -= amount
            acc2.balance += amount
```
Since every thread acquires locks in strictly increasing order, circular wait is mathematically impossible.

---

## 3. Database Internals & Transaction Isolation

### Q3: B+ Trees vs. Log-Structured Merge (LSM) Trees
**Question:** Compare B+ Trees (e.g. InnoDB, PostgreSQL) and LSM Trees (e.g. RocksDB, Cassandra). When should you choose an LSM Tree over a B+ Tree?

**Deep Explanation:**
| Dimension | B+ Tree | LSM Tree |
| :--- | :--- | :--- |
| **Write Pattern** | In-place page updates; random disk I/O | Append-only sequential writes (MemTable $\to$ SSTable) |
| **Write Amplification** | High (writing a single 32-byte row writes full 16KB page) | Moderate to High (due to background compaction) |
| **Read Latency** | Outstanding ($O(\log N)$ bounded page reads) | Variable (must check MemTable, Bloom filters, SSTables) |
| **Storage Compression** | Poor (page fragmentation, 30% fill factor slack) | Exceptional (immutable sorted SSTables compress densely) |
| **Optimal Workload** | Read-heavy, OLTP transactions, range scans | Write-heavy, time-series, append-only telemetry |

**Decision Threshold:**
Choose an LSM Tree when write throughput is the primary system bottleneck, or when storage cost on NVMe SSDs requires aggressive delta compression.

---

### Q4: Read Committed vs. Repeatable Read vs. Serializable Isolation
**Question:** Explain the difference between Non-Repeatable Reads and Phantom Reads. How does Snapshot Isolation (MVCC) prevent them without read locks?

**Deep Explanation:**
- **Non-Repeatable Read:** Transaction $T_1$ reads a row. Transaction $T_2$ updates that row and commits. $T_1$ reads the row again and sees the updated value.
- **Phantom Read:** Transaction $T_1$ executes a range query (`WHERE age > 30`). Transaction $T_2$ inserts a *new* row with `age = 35` and commits. $T_1$ re-executes the query and sees a new "phantom" row.

**Snapshot Isolation via Multi-Version Concurrency Control (MVCC):**
Under MVCC (Postgres, MySQL InnoDB):
1. When transaction $T_1$ begins, it is assigned a read timestamp $T_{\text{read}} = \text{TxID}$.
2. Rows carry visibility metadata: `xmin` (creation TxID) and `xmax` (deletion/superseding TxID).
3. A row is visible to $T_1$ if and only if:
   $$xmin \le T_{\text{read}} \land (xmax > T_{\text{read}} \lor xmax = \text{uncommitted})$$
4. Readers read immutable historical snapshots without taking read locks. Concurrent writes create a new version of the row with a higher timestamp; readers remain completely unblocked and isolated from uncommitted or concurrent changes.

---

## 4. Distributed Systems & Microservices Architecture

### Q5: Microservices Resiliency: Circuit Breakers & Sagas
**Question:** How does a Michael Nygard Circuit Breaker prevent cascading failures in a microservices mesh? Describe its three finite state machine states.

**Deep Explanation:**
A Circuit Breaker wraps remote RPC calls to prevent a failing downstream dependency from exhausting upstream thread pools and connection queues.

```
       +---------------------------------------------+
       |                                             | Success Reset
       v                                             |
   [ CLOSED ] --- Failure Threshold Exceeded ---> [ OPEN ]
       ^                                             |
       |                   Timeout Expired           |
       |                         v                   |
       +----- Success ----- [ HALF-OPEN ] <----------+
```

1. **CLOSED (Normal Operation):** All traffic passes to downstream. Failures are tracked. If failure rate exceeds threshold (e.g., 5 consecutive errors), breaker trips to **OPEN**.
2. **OPEN (Fast-Fail):** All requests fail immediately with an error or fallback response without invoking the remote service. Preserves downstream resources and prevents upstream caller timeouts.
3. **HALF-OPEN (Canary Probe):** After a cooldown period (e.g., 30s), a limited trial probe of requests is permitted through. If they succeed, the breaker resets to **CLOSED**. If any fail, it trips back to **OPEN**.

---

## 5. Coding Exercise: Production Token Bucket Rate Limiter
**Question:** Implement a thread-safe, memory-efficient Token Bucket Rate Limiter that permits bursts while enforcing an average rate limit.

**Solution:**
```python
import time
import threading

class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_rate_per_sec: float):
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        self.tokens = float(capacity)
        self.last_refill_time = time.time()
        self.lock = threading.Lock()

    def allow_request(self, tokens_needed: int = 1) -> bool:
        with self.lock:
            now = time.time()
            # Calculate elapsed time and add replenished tokens
            elapsed = now - self.last_refill_time
            self.tokens = min(float(self.capacity), self.tokens + elapsed * self.refill_rate)
            self.last_refill_time = now

            if self.tokens >= tokens_needed:
                self.tokens -= tokens_needed
                return True
            return False

# Verification
limiter = TokenBucketRateLimiter(capacity=5, refill_rate_per_sec=10.0)
# Burst of 5 requests should pass
for _ in range(5):
    assert limiter.allow_request() is True
# 6th request immediate burst should fail
assert limiter.allow_request() is False
# Wait 100ms: 1 token refilled (10 * 0.1 = 1.0)
time.sleep(0.12)
assert limiter.allow_request() is True
```
