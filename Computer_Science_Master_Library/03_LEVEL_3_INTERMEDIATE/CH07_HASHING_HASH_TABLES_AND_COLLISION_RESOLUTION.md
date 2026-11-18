# Chapter 07: Hashing, Hash Tables, and Collision Resolution

---

## 1. Executive Summary & Core Concept

When storing and retrieving key-value pairs, comparison-based search structures (such as balanced binary search trees or skip lists) require $\mathcal{O}(\log n)$ time because every lookup must traverse multiple decision branches. In high-performance software—such as database indices, web caches, symbol tables in compilers, and routing dictionaries—even logarithmic time is insufficient. Systems demand **constant-time $\mathcal{O}(1)$ retrieval**.

**Hashing** solves this challenge by transforming an arbitrary key (such as a string username or 64-bit integer) into a bounded numerical array index using a mathematical function known as a **Hash Function**:
$$h: U \to \{0, 1, \dots, m - 1\}$$
where $U$ is the universe of all possible keys and $m$ is the table size.

Because the key universe $U$ is vastly larger than the table size $m$ ($|U| \gg m$), the **Pigeonhole Principle** guarantees that collisions—where two distinct keys hash to the exact same slot ($h(k_1) = h(k_2)$)—are mathematically inevitable. 

This chapter examines:
- The design of uniform hash functions (Division, Multiplication, MurmurHash3, and SipHash).
- The two fundamental collision resolution paradigms: **Separate Chaining** and **Open Addressing** (Linear Probing, Quadratic Probing, and Double Hashing).
- The critical role of the **Load Factor** ($\alpha = n/m$) and dynamic rehashing.
- Advanced modern collision strategies: **Robin Hood Hashing** and **Cuckoo Hashing** ($\mathcal{O}(1)$ guaranteed worst-case lookup).
- Defense against **Algorithmic Complexity Attacks (Hash-Flooding DoS)**.

---

## 2. Prerequisites & Cognitive Map

```mermaid
graph TD
    A[Level 2 CH02: Bitwise Math & Types] --> B[Level 2 CH07: Dynamic Heap Memory malloc/realloc]
    B --> C[Level 3 CH01: Asymptotic Analysis & Amortization]
    C --> D[Level 3 CH02: Arrays & Linked Lists]
    D --> E[Level 3 CH07: Hashing & Hash Tables]
    E --> F[Level 3 CH08: Sorting & Partitioning]
    E --> G[Level 4: Distributed Hash Tables & Consistent Hashing]
```

### Required Knowledge Checklist
- Bitwise operators (`<<`, `>>`, `^`, `&`) and modular arithmetic.
- Dynamic array resizing with geometric doubling from Chapter 02.
- Singly linked list pointer manipulation from Chapter 02.

---

## 3. The "Explain Like I'm Five" (ELI5) Analogy

### The Post Office Mailboxes and The Coat Check Ticket
- **Why We Need Hashing**:
  Imagine a university with 50,000 students, and the registrar wants to store student files.
  - **Direct Addressing (Naive)**: Create 10-digit file drawers numbered 0000000000 to 9999999999 (matching each student's phone number). You would need **10 billion empty drawers** to hold only 50,000 files! Most drawers would sit completely empty, wasting acres of warehouse space.
  - **A Hash Function**: You buy a neat cabinet with 100 drawers. When a student named "Aarav" walks in, you run their name through a fun mathematical blender (the Hash Function) that scrambles the letters and outputs drawer #42. Whenever Aarav comes back, you run his name through the exact same blender—it outputs drawer #42 again, and you grab his file in 1 second!
- **A Collision (Two People, One Drawer)**:
  What if "Priya" also scrambles to drawer #42?
  - **Separate Chaining (The Drawer Folder Chain)**: Drawer #42 has a string inside it. You clip Aarav's file to the string, and you clip Priya's file right behind it. When you open drawer #42, you scan the string of clips.
  - **Open Addressing (The Polite Neighbor Rule)**: Drawer #42 is already occupied by Aarav! Priya smiles, walks down the hall, and checks drawer #43. If drawer #43 is empty, she takes it!

---

## 4. Formal Mathematical & Theoretical Foundations

### 4.1 The Pigeonhole Principle & Inevitability of Collisions
Let $U$ be the universe of possible keys, and let $T[0 \dots m-1]$ be a hash table of size $m$.
If $|U| > m$, then by the Pigeonhole Principle, there must exist at least two distinct keys $k_1, k_2 \in U$ ($k_1 \ne k_2$) such that:
$$h(k_1) = h(k_2)$$

### 4.2 Hash Function Design Methodologies
A good hash function must satisfy the **Simple Uniform Hashing Assumption (SUHA)**: any given key is equally likely to hash into any of the $m$ slots, independently of where any other key has hashed.

#### 1. The Division Method
$$h(k) = k \pmod m$$
- **Rule for $m$**: $m$ should be a **prime number** not too close to an exact power of 2 ($m \ne 2^p - 1$). Choosing a power of 2 ($m = 2^p$) means $h(k)$ simply extracts the lowest $p$ bits of $k$, ignoring all higher-order entropy and clustering patterns!

#### 2. The Multiplication Method (Knuth)
Let $A$ be a constant real fraction in the range $0 < A < 1$.
$$h(k) = \lfloor m (k A \pmod 1) \rfloor = \lfloor m (k A - \lfloor k A \rfloor) \rfloor$$
Donald Knuth suggested using the fractional part of the Golden Ratio:
$$A = \frac{\sqrt{5} - 1}{2} \approx 0.6180339887\dots$$
- **Advantage**: The value of $m$ is not critical; it can be chosen as an exact power of two ($m = 2^p$), allowing fast bitwise shifts:
  $$h(k) = (k \times s) \gg (w - p)$$
  where $s = \lfloor A \cdot 2^w \rfloor$ and $w$ is the machine word width (32 or 64 bits).

#### 3. Universal Hashing (Provable Collision Protection)
Let $\mathcal{H}$ be a finite collection of hash functions mapping $U \to \{0, \dots, m-1\}$.
$\mathcal{H}$ is **Universal** if for every pair of distinct keys $k, l \in U$ ($k \ne l$), the number of hash functions $h \in \mathcal{H}$ for which $h(k) = h(l)$ is at most $\frac{|\mathcal{H}|}{m}$:
$$\Pr_{h \in \mathcal{H}}[h(k) = h(l)] \le \frac{1}{m}$$
If an application picks a random function $h \in \mathcal{H}$ at startup, no fixed malicious input dataset can force worst-case behavior!

---

### 4.3 Load Factor and Complexity Bounds (Under SUHA)
The **Load Factor** $\alpha$ of a hash table with $n$ keys and $m$ slots is:
$$\alpha = \frac{n}{m}$$

#### Separate Chaining Bounds:
- Under SUHA, the average length of any chain is exactly $\alpha$.
- Expected time for an unsuccessful search: $\Theta(1 + \alpha)$.
- Expected time for a successful search: $\Theta(1 + \alpha / 2) = \Theta(1 + \alpha)$.
- If $m \propto n \implies \alpha = \mathcal{O}(1)$, lookups execute in **$\mathcal{O}(1)$ average time**.

#### Open Addressing Bounds ($\alpha < 1$ strictly required):
- In open addressing, every slot holds at most 1 element ($\alpha \le 1$).
- Under uniform hashing, the expected number of probes in an **unsuccessful search** is:
  $$E[\text{Probes}_{\text{unsuccessful}}] \le \frac{1}{1 - \alpha}$$
  - For $\alpha = 0.50$: $\le \frac{1}{1 - 0.5} = \mathbf{2\text{ probes}}$.
  - For $\alpha = 0.90$: $\le \frac{1}{1 - 0.9} = \mathbf{10\text{ probes}}$.
  - For $\alpha = 0.99$: $\le \frac{1}{1 - 0.99} = \mathbf{100\text{ probes}}$.
- This demonstrates why open-addressed tables MUST resize when $\alpha$ exceeds $0.70$–$0.75$.

---

## 5. Architectural & Hardware Context

```
Collision Strategy Comparison: Memory Architecture & Hardware Caches
========================================================================
Separate Chaining (Linked Nodes):
Table Array [ 0 ] ---> [ Key A | Val A | Next ] ---> [ Key B | Val B | NULL ]
            [ 1 ] ---> NULL
            [ 2 ] ---> [ Key C | Val C | Next ]
Result: Cache-unfriendly pointer chasing across random heap addresses.

Open Addressing with Linear Probing:
Table Array: [ Key A | Val A ][ Key B | Val B ][ Key C | Val C ][ Empty ]
Result: Sequential scanning of contiguous array slots!
Hardware CPU L1 cache prefetcher streams consecutive slots in 1 single memory fetch!
```

### Why Open Addressing Dominates Modern Systems
In the 1980s, Separate Chaining was standard. On modern CPUs, where a DRAM access costs 100 ns but an L1 cache hit costs 1 ns, **Linear Probing is significantly faster than Separate Chaining** for tables under $70\%$ load factor because probing adjacent slots generates **zero cache misses**.

---

## 6. Core Collision Resolution Paradigms

### 6.1 Separate Chaining
Each slot in the array contains a pointer to a linked list (or balanced binary tree) of entries that hash to that slot.

```c
typedef struct HashNode {
    char *key;
    int value;
    struct HashNode *next;
} HashNode;

typedef struct {
    HashNode **buckets;
    size_t capacity;
    size_t size;
} ChainedHashTable;
```

---

### 6.2 Open Addressing: Probe Sequences
In Open Addressing, all elements reside directly within the array $T[0 \dots m-1]$. The hash function is extended to take a probe number $i \in \{0, 1, \dots, m-1\}$:
$$h: U \times \{0, 1, \dots, m-1\} \to \{0, 1, \dots, m-1\}$$

#### 1. Linear Probing
$$h(k, i) = (h'(k) + i) \pmod m$$
- **Advantage**: Optimal CPU cache line utilization.
- **Flaw: Primary Clustering**: Long contiguous runs of occupied slots build up over time. Any key hashing into the cluster extends it further, degrading search time to $\mathcal{O}(n)$.

#### 2. Quadratic Probing
$$h(k, i) = (h'(k) + c_1 i + c_2 i^2) \pmod m$$
- Reduces primary clustering by jumping quadratically, but suffers from **Secondary Clustering** (keys with the same initial hash $h'(k)$ trace identical probe paths).

#### 3. Double Hashing (The Gold Standard of Open Addressing)
Uses two independent auxiliary hash functions $h_1(k)$ and $h_2(k)$:
$$h(k, i) = (h_1(k) + i \cdot h_2(k)) \pmod m$$
- $h_2(k)$ must produce a step size relatively prime to $m$ (typically $m$ is prime and $h_2(k) = 1 + (k \pmod{m - 1})$).
- Probe sequences depend on both $h_1$ and $h_2$, completely eliminating primary and secondary clustering!

---

## 7. Advanced Modern Hashing Architectures

### 7.1 Robin Hood Hashing
In standard linear probing, an element inserted early stays close to its home slot, while a late-arriving element may be pushed dozens of slots away, creating high variance in lookup times.
**Robin Hood Hashing** enforces fairness: *"Take from the rich and give to the poor."*
- Every element tracks its **Probe Sequence Length (PSL)**: the distance from its original home hash slot.
- During insertion, if the incoming element has a larger PSL than the element currently occupying the slot (meaning the incoming element is "poorer"), the incoming element takes the slot, and the incumbent element is displaced and sifts forward!
- **Benefit**: Drastically reduces variance in search times and allows tables to run safely at up to **$90\%$ load factor**.

### 7.2 Cuckoo Hashing
Invented by Rasmus Pagh and Flemming Friche Rodler (2001), Cuckoo Hashing uses **two independent hash functions** $h_1(k)$ and $h_2(k)$ and two separate tables:
- A key $k$ can reside in ONLY two possible locations: $T_1[h_1(k)]$ or $T_2[h_2(k)]$.
- **Lookup**: Inspect $T_1[h_1(k)]$ and $T_2[h_2(k)]$. Total lookups $= \mathbf{2\text{ memory accesses worst-case } (\mathcal{O}(1))}$!
- **Insertion**: Insert into $T_1[h_1(k)]$. If occupied by key $y$, kick $y$ out (like a cuckoo bird kicks eggs out of a nest) and insert $y$ into its alternative location in $T_2[h_2(y)]$. If infinite loops occur, rehash the entire table with new random hash functions.

---

## 8. Visual Models & Deep Walkthroughs

### Open Addressing: Deletion with Tombstones (`DELETED`)

Why can't we simply set a deleted slot to `NULL` (empty) in linear probing?

```
Array State:
Slot 0: [ Key A (h=0) ]
Slot 1: [ Key B (h=0, probed +1) ]
Slot 2: [ Key C (h=0, probed +2) ]
Slot 3: [ EMPTY ]
```

1. If we delete `Key B` by setting Slot 1 to `EMPTY`:
   ```
   Slot 0: [ Key A ]
   Slot 1: [ EMPTY ]   <-- Erased!
   Slot 2: [ Key C ]
   ```
2. Now search for `Key C` ($h=0$).
   - Probe 0: Hits `Key A` (No match).
   - Probe 1: Hits `EMPTY`!
   - **FATAL ERROR**: Linear probing terminates search when an empty slot is encountered, concluding that `Key C` does not exist!
3. **The Tombstone Solution**: Set Slot 1 to a special sentinel `TOMBSTONE` (or `DELETED`).
   - Searches skip over `TOMBSTONE`s and continue probing.
   - Insertions can overwrite `TOMBSTONE`s with new keys.

---

## 9. Common Pitfalls, Anti-Patterns & Undefined Behavior

| Anti-Pattern / Bug | Code Example | Consequence / Fix |
|:---|:---|:---|
| **Power of Two Table with Division Hash**| `h = k % 1024;` | Uses only lowest 10 bits; severe clustering if keys share low-order patterns. Use prime table size or multiplication hash. |
| **Forgetting to Rehash on Growth** | `realloc(table, new_cap);` without rehashing | Elements reside at wrong hash modulo positions! Table must allocate new buffer and re-insert every key. |
| **Step Size Zero in Double Hashing** | $h_2(k) = 0$ | $h(k, i) = h_1(k) + i \cdot 0 = h_1(k)$. Infinite loop on collision! Ensure $h_2(k) \ge 1$. |
| **Modifying Key While Stored in Table** | Mutating string key in-place | Hash code changes; element becomes permanently un-findable (Orphaned entry / Memory leak). |

---

## 10. Industrial & Production Application

### Case 1: Python's Compact Dict Architecture (PyPy / Python 3.6+)
Historically, Python dictionaries stored an array of 24-byte entries (`hash`, `key`, `value`). With empty slots accounting for 30–50% of the table, this wasted megabytes of memory.
In Python 3.6, Raymond Hettinger redesigned `dict`:
1. **Indices Array**: A small, compact sparse array of 1-byte integers: `[-1, 0, -1, 1, 2]`.
2. **Entries Array**: A dense, contiguous array holding only active entries in order of insertion.
- **Result**: Reduced memory footprint by **$35\%$**, and made Python dictionaries preserve insertion order by default!

### Case 2: Java 8 `HashMap` Treeification
In Java 8, when a Separate Chaining bucket exceeds `TREEIFY_THRESHOLD = 8` entries and table capacity $\ge 64$, the linked list is dynamically transformed into a **Red-Black Tree**. Lookups in that bucket drop from linear $\mathcal{O}(n)$ to logarithmic $\mathcal{O}(\log n)$, neutralizing Hash-Flooding DoS attacks.

---

## 11. Benchmarks, Complexity & Performance Profiling

| Collision Strategy | Average Search | Worst-Case Search | Average Insert | Cache Performance | Max Safe Load Factor ($\alpha$) |
|:---|:---|:---|:---|:---|:---|
| **Separate Chaining** | $\Theta(1)$ | $\mathcal{O}(n)$ | $\Theta(1)$ | Poor | $\alpha \approx 1.0 - 2.0$ |
| **Linear Probing** | $\mathbf{\Theta(1)}$ | $\mathcal{O}(n)$ | $\Theta(1)$ | **Optimal** | $\alpha \le 0.70$ |
| **Double Hashing** | $\mathbf{\Theta(1)}$ | $\mathcal{O}(n)$ | $\Theta(1)$ | Moderate | $\alpha \le 0.80$ |
| **Robin Hood Hashing**| $\mathbf{\Theta(1)}$ | $\mathcal{O}(\log n)$ | $\Theta(1)$ | **Optimal** | $\alpha \le 0.90$ |
| **Cuckoo Hashing** | $\mathbf{\mathcal{O}(1)}$ (Strict) | $\mathbf{\mathcal{O}(1)}$ (Strict) | $\mathcal{O}(1)$ amortized | Good | $\alpha \le 0.50$ |

---

## 12. Security Implications & Vulnerability Analysis

### Hash-Flooding Denial of Service (CVE-2011-4885) & SipHash
In 2011, researchers demonstrated that standard non-cryptographic hash functions (like MurmurHash, Jenkins, and Java's default `String.hashCode()`) are linearly vulnerable to multicollision generation.

```python
# A simple string hash: hash = 31 * hash + char
# An attacker generates 50,000 strings that all evaluate to the same hash integer!
# Submitting them in a single HTTP POST request freezes servers for 10 minutes.
```

### The Universal Defense: SipHash-2-4
Invented by Jean-Philippe Aumasson and Daniel J. Bernstein (2012), **SipHash** is a cryptographically secure, pseudorandom 64-bit keyed hash function designed specifically for hash table lookups:
- On process startup, the runtime generates a secret 128-bit random key from the OS CSPRNG (`/dev/urandom`):
  $$k = (k_0, k_1)$$
- Even if an attacker knows the algorithm, they cannot precompute collisions without knowing the process's secret key!
- SipHash is now the mandatory default hash function in Python, Rust, Ruby, and the Linux kernel.

---

## 13. Edge Cases & Boundary Conditions

1. **Rehashing Infinite Loops in Cuckoo Hashing**: When cycle collisions occur, Cuckoo insertion must abort after a fixed threshold (e.g. $50$ kicks) and rebuild the table with fresh random seed functions.
2. **Deleting All Elements in Open Addressing**: A table filled with tombstones exhibits $\alpha = 0$ active elements, but search probes will traverse every single tombstone! The table must trigger rehashing when the tombstone count exceeds a set limit.
3. **Negative Hash Codes**: In C/Java, `%` on signed integers can return negative numbers (`-5 % 4 = -1`). Always mask sign bits:
   `size_t slot = ((size_t)hash_code) % capacity;`

---

## 14. Comparative Analysis: Hash Tables vs Balanced BSTs

| Feature | Hash Table | Balanced BST (Red-Black / AVL) |
|:---|:---|:---|
| **Average Lookup Time**| $\mathbf{\mathcal{O}(1)}$ | $\mathcal{O}(\log n)$ |
| **Worst-Case Lookup** | $\mathcal{O}(n)$ (or $\mathcal{O}(1)$ in Cuckoo) | $\mathbf{\mathcal{O}(\log n)}$ (Guaranteed) |
| **Key Ordering** | Unordered (Randomized order) | **Strictly Sorted Order** |
| **Range Queries** | $\mathcal{O}(n)$ (Must scan all keys) | $\mathbf{\mathcal{O}(\log n + K)}$ (In-order walk) |
| **Find Min / Max** | $\mathcal{O}(n)$ (Full scan) | $\mathbf{\mathcal{O}(\log n)}$ |
| **Memory Overhead** | Sparsity / Padding buffers | 2–3 pointers per node |

---

## 15. Emerging Paradigms, AI & Future Perspectives

1. **Sub-Fingerprinted SIMD Swiss Tables (Google Abseil)**: Google's `absl::flat_hash_map` uses a control byte array holding 7-bit metadata "fingerprints" for each slot. A single 128-bit SSE2 instruction (`_mm_cmpeq_epi8`) compares 16 slots simultaneously in **1 CPU cycle**, eliminating branch instructions during linear probing!
2. **AI Learned Hash Functions**: Neural network hashing models learn the empirical distribution of real-world keys, synthesizing non-uniform hash functions that achieve zero collisions on specific production datasets.

---

## 16. Step-by-Step Solved Problem 1 (Foundational / Academic)

### Problem Statement
Given a hash table of size $m = 7$ using the hash function $h(k) = k \pmod 7$, insert keys:
$$[10, \quad 17, \quad 24, \quad 31]$$
using:
1. Separate Chaining.
2. Linear Probing ($h(k, i) = (h(k) + i) \pmod 7$).

### 1. Separate Chaining Trace:
- $h(10) = 10 \pmod 7 = 3 \to \text{Bucket } 3: [10]$.
- $h(17) = 17 \pmod 7 = 3 \to \text{Collision! Prepend to Bucket } 3: [17 \to 10]$.
- $h(24) = 24 \pmod 7 = 3 \to \text{Collision! Prepend to Bucket } 3: [24 \to 17 \to 10]$.
- $h(31) = 31 \pmod 7 = 3 \to \text{Collision! Prepend to Bucket } 3: [31 \to 24 \to 17 \to 10]$.
- **Result**: All 4 keys clustered into Bucket 3! (Illustrating why choosing a bad prime or bad step creates list degradation).

### 2. Linear Probing Trace:
- $h(10) = 3 \to \text{Slot 3 is empty} \to T[3] = 10$.
- $h(17) = 3 \to \text{Slot 3 occupied} \to \text{Probe } (3+1)\%7 = 4 \to T[4] = 17$.
- $h(24) = 3 \to \text{Slots 3, 4 occupied} \to \text{Probe } (3+2)\%7 = 5 \to T[5] = 24$.
- $h(31) = 3 \to \text{Slots 3, 4, 5 occupied} \to \text{Probe } (3+3)\%7 = 6 \to T[6] = 31$.
- **Resulting Table Array**:
  `T = [NULL, NULL, NULL, 10, 17, 24, 31]`
  Demonstrates Primary Clustering!

---

## 17. Step-by-Step Solved Problem 2 (Algorithmic / Systems Level)

### Problem Statement
Implement an Open-Addressed Hash Table in C with Linear Probing supporting `insert`, `search`, and `delete` using Tombstone markers, automatically resizing when load factor $\alpha \ge 0.70$.

### Code Implementation
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define TOMBSTONE ((char *)-1)

typedef struct {
    char *key;
    int val;
} Entry;

typedef struct {
    Entry *entries;
    size_t capacity;
    size_t count;
} LinearHashTable;

static uint32_t hash_djb2(const char *s) {
    uint32_t h = 5381;
    while (*s) h = ((h << 5) + h) + (unsigned char)*s++;
    return h;
}

LinearHashTable* ht_create(size_t cap) {
    LinearHashTable *ht = (LinearHashTable *)malloc(sizeof(LinearHashTable));
    ht->capacity = cap;
    ht->count = 0;
    ht->entries = (Entry *)calloc(cap, sizeof(Entry));
    return ht;
}

static void ht_resize(LinearHashTable *ht) {
    size_t old_cap = ht->capacity;
    Entry *old_entries = ht->entries;

    ht->capacity = old_cap * 2;
    ht->count = 0;
    ht->entries = (Entry *)calloc(ht->capacity, sizeof(Entry));

    for (size_t i = 0; i < old_cap; ++i) {
        if (old_entries[i].key != NULL && old_entries[i].key != TOMBSTONE) {
            // Re-insert into expanded table
            uint32_t slot = hash_djb2(old_entries[i].key) % ht->capacity;
            while (ht->entries[slot].key != NULL) {
                slot = (slot + 1) % ht->capacity;
            }
            ht->entries[slot] = old_entries[i];
            ht->count++;
        }
    }
    free(old_entries);
}

bool ht_insert(LinearHashTable *ht, const char *key, int val) {
    if ((double)(ht->count + 1) / ht->capacity >= 0.70) {
        ht_resize(ht);
    }

    uint32_t slot = hash_djb2(key) % ht->capacity;
    size_t first_tombstone = (size_t)-1;

    while (ht->entries[slot].key != NULL) {
        if (ht->entries[slot].key == TOMBSTONE) {
            if (first_tombstone == (size_t)-1) first_tombstone = slot;
        } else if (strcmp(ht->entries[slot].key, key) == 0) {
            ht->entries[slot].val = val; // Key exists, update value
            return true;
        }
        slot = (slot + 1) % ht->capacity;
    }

    // Insert at tombstone if available, else at empty slot
    size_t dest_slot = (first_tombstone != (size_t)-1) ? first_tombstone : slot;
    ht->entries[dest_slot].key = strdup(key);
    ht->entries[dest_slot].val = val;
    ht->count++;
    return true;
}
```

---

## 18. Step-by-Step Solved Problem 3 (Industry / Production Debugging)

### Production Incident Scenario
A distributed cache cluster experiences severe memory leaks and latency degradation after migrating from a static array to an open-addressed hash map.

### Root Cause Analysis
```c
// VULNERABLE DELETION IMPLEMENTATION:
bool ht_delete(LinearHashTable *ht, const char *key) {
    size_t slot = hash(key) % ht->capacity;
    while (ht->entries[slot].key != NULL) {
        if (strcmp(ht->entries[slot].key, key) == 0) {
            // BUG: Developer forgot to free strdup'd string!
            ht->entries[slot].key = TOMBSTONE;
            ht->count--;
            return true;
        }
        slot = (slot + 1) % ht->capacity;
    }
    return false;
}
```
1. `strdup()` allocated heap memory for `key`.
2. Overwriting `ht->entries[slot].key` with `TOMBSTONE` without calling `free(ht->entries[slot].key)` permanently leaked the key string on every deletion!
3. Across 50 million deletions, 2 GB of memory leaked, and tombstone accumulation forced lookups to scan thousands of dead slots.

### Production Fix: Explicit Free and Tombstone Reclaim Threshold
```c
free(ht->entries[slot].key); // Free string memory!
ht->entries[slot].key = TOMBSTONE;
ht->tombstone_count++;

// If tombstones exceed 25% of table capacity, force a compacting rehash!
if (ht->tombstone_count > ht->capacity / 4) {
    ht_rehash_compact(ht);
}
```

---

## 19. Categorized Practice Exercises

### Beginner (Confidence Builders)
1. Write a function to implement the DJB2 string hashing algorithm in C.
2. Given table size $m = 11$, insert keys `22, 1, 13, 11, 24, 33` using linear probing.
3. Why must the second hash function $h_2(k)$ in double hashing never evaluate to zero?

### Intermediate (Exam Level)
4. Implement a hash map with Separate Chaining and dynamic capacity doubling when load factor $\alpha > 1.0$.
5. Write a function to check if two strings are valid anagrams of each other in $\mathcal{O}(n)$ time and $\mathcal{O}(1)$ auxiliary space using an integer frequency hash array.
6. Design an $\mathcal{O}(1)$ average time `RandomizedSet` that supports `insert()`, `remove()`, and `get_random()` using a hash map combined with a dynamic array.

### Advanced (Systems / Competitive)
7. Implement **Robin Hood Hashing** in C, recording Probe Sequence Length (PSL) per entry and displacing richer elements during insertion.
8. Implement **Cuckoo Hashing** using two tables and two independent hash functions, detecting insertion cycles and triggering dynamic rehashing.

---

## 20. University Exam Practice Questions (SPPU / International Style)

### Question 1 (Theory - 5 Marks)
Define Hashing. Explain the concept of collision. Differentiate between Open Addressing and Separate Chaining with suitable diagrams.

### Question 2 (Numerical - 5 Marks)
A hash table of size $m = 11$ uses open addressing with double hashing:
$$h_1(k) = k \pmod{11}$$
$$h_2(k) = 1 + (k \pmod{10})$$
Insert the keys: $k = 27, 43, 692, 72$ into an initially empty table and show the contents of each slot after each insertion.

### Question 3 (Performance & Load Factor - 5 Marks)
Define the Load Factor ($\alpha$) of a hash table. Derive the expected number of probes for an unsuccessful search in open addressing under uniform hashing:
$$E = \frac{1}{1 - \alpha}$$

---

## 21. Industry Interview Masterclass

### Tier A (Freshers / Campus Hiring)
- **Q**: What is the difference between $\mathcal{O}(1)$ average time and $\mathcal{O}(1)$ worst-case time in a hash table?
- **A**: A hash table achieves $\mathcal{O}(1)$ time on average under uniform hashing when collisions are rare. However, in the worst case (e.g. all keys hash to the same bucket, or all open slots are clustered), lookups degrade to linear $\mathcal{O}(n)$ time.

### Tier B (Mid-Level Engineers)
- **Q**: What is the purpose of Tombstone markers in Open Addressing deletion?
- **A**: In open addressing, linear or double probing continues searching until it finds the key or encounters an empty (`NULL`) slot. If a deleted item were replaced with an empty slot, subsequent searches for keys that probed past that slot would terminate prematurely and report that the key does not exist. Tombstones act as "occupied" markers for searches (allowing probing to continue) but act as "empty" slots for new insertions.

### Tier C (Senior Systems Engineers)
- **Q**: Why does Google's Abseil `flat_hash_map` (Swiss Table) outperform traditional open addressing hash maps?
- **A**: Traditional open addressing stores full keys inside the table array, causing cache misses when comparing keys during probing. Swiss Tables maintain a separate parallel array of 1-byte control metadata storing a 7-bit hash fingerprint. Using 128-bit SIMD instructions (`_mm_cmpeq_epi8`), the CPU probes 16 metadata slots simultaneously in a single clock cycle, comparing full keys only when a fingerprint matches.

### Tier D (FAANG / Core Systems & Kernel)
- **Q**: What is a Hash-Flooding Denial of Service attack, and how does SipHash neutralize it?
- **A**: In web applications parsing user parameters (JSON/HTTP POST), attackers send thousands of crafted strings that generate the same hash code in deterministic algorithms (e.g. Java's `s[0]*31^(n-1)` or MurmurHash), degrading hash tables to an $\mathcal{O}(n^2)$ linear chain search and consuming 100% CPU. SipHash is a cryptographically strong pseudorandom function initialized with a secret random 128-bit key generated per-process on startup. Without knowing the secret key, attackers cannot precompute colliding inputs.

---

## 22. Hands-on Lab Assignment & Verification Checklist

### Lab Goal
Write a comprehensive hash table laboratory suite in C and Python that:
1. Implements Linear Probing with Tombstone deletion and dynamic resizing at $\alpha \ge 0.70$.
2. Implements Separate Chaining and benchmarks throughput under uniform vs. colliding inputs.
3. Validates SipHash pseudorandom distribution properties.
4. Demonstrates Robin Hood Hashing variance reduction.

### Verification Checklist
- [x] Tombstone deletion preserves search paths for subsequently inserted colliding keys.
- [x] Dynamic resizing rehashes all active elements and clears tombstones.
- [x] SipHash generates uniform distribution across all 64 bits.
- [x] All simulation and test scripts execute with exit code 0.

---

## 23. High-Yield Quick Revision Summary

| Method | Probe Function | Primary Advantage | Major Weakness |
|:---|:---|:---|:---|
| **Separate Chaining** | N/A (Linked lists) | Simple; handles $\alpha > 1.0$ | Cache-unfriendly pointer chasing |
| **Linear Probing** | $(h'(k) + i) \pmod m$ | **Optimal CPU cache hits** | Primary Clustering |
| **Quadratic Probing** | $(h'(k) + c_1 i + c_2 i^2) \pmod m$ | Eliminates primary clustering | Secondary Clustering |
| **Double Hashing** | $(h_1(k) + i \cdot h_2(k)) \pmod m$ | Eliminates all clustering | Higher hashing computation |
| **Robin Hood** | Linear probing + PSL swaps | Minimizes probe variance | Higher insertion latency |
| **Cuckoo Hashing** | 2 tables: $T_1[h_1], T_2[h_2]$ | **$\mathcal{O}(1)$ worst-case lookup** | Insertion cycles require full rehash |

---

## 24. Verified Academic Citations & Authoritative References

1. **Knuth, D. E.** (1998). *The Art of Computer Programming, Volume 3: Sorting and Searching* (2nd ed.). Addison-Wesley. [Section 6.4: Hashing, pp. 513–558].
2. **Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C.** (2022). *Introduction to Algorithms* (4th ed.). MIT Press. [Chapter 11: Hash Tables, pp. 272–311].
3. **Pagh, R., & Rodler, F. F.** (2004). *Cuckoo Hashing*. Journal of Algorithms, 51(2), pp. 122–144.
4. **Aumasson, J. P., & Bernstein, D. J.** (2012). *SipHash: A Fast Short-Input PRF*. Progress in Cryptology — INDOCRYPT 2012, pp. 489–508.
