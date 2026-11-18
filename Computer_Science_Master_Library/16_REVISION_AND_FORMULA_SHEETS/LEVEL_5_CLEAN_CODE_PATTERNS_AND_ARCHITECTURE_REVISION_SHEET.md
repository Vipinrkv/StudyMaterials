# Level 5 Revision & Formula Sheet: Clean Code, Design Patterns, Web Architecture & Security

---

## 1. Quick Reference: Chapters 01 to 05

| Chapter | Core Focus | Key Axioms & Formulas | Primary Pitfalls / Edge Cases |
|:---|:---|:---|:---|
| **CH01: Clean Code & SOLID** | Single Responsibility, OCP, LSP, ISP, DIP | $M = E - V + 2P = \pi + 1$; $I = \frac{C_e}{C_a + C_e}$; $D = \|A + I - 1\|$ | Strengthening preconditions in subtypes; God objects; tight coupling |
| **CH02: Creational & Structural Patterns** | Abstract Factory, Builder, Singleton, Decorator | $\mathcal{O}(N)$ vs $\mathcal{O}(2^N)$ subclassing; DCL `volatile` memory fence | Singleton as global mutable state; telescoping constructors |
| **CH03: Behavioral & Enterprise Patterns**| Strategy, Observer, State FSM, Unit of Work | $\delta(s, e) \in S$; $\text{Flush} = \mathcal{N} \cup \mathcal{D} \cup \mathcal{R}$; Identity Map | Memory leaks in observers (unclosed subscriptions); leaky repositories |
| **CH04: Web Architecture & API Protocols**| REST, GraphQL, gRPC, DataLoader, HTTP/1-3 | $f(f(x)) = f(x)$ (Idempotency); $\text{Tag} = (F \ll 3) \mid W$; $\mathcal{O}(1)$ batch | GraphQL N+1 queries; unbounded query depth DOS; head-of-line blocking |
| **CH05: Application Security & Auth** | OWASP Top 10, JWT HS256/RS256, Token Bucket | $T = \min(C, T + \Delta t \cdot r)$; $\text{Argon2id}(P, S, t, m, p)$; Constant-time cmp | IDOR vulnerabilities; JWT `alg: none` attack; storing tokens in `localStorage` |

---

## 2. Software Architecture & Metric Invariants

### 2.1 McCabe's Cyclomatic Complexity
$$M = E - V + 2P = \pi + 1$$
- $\pi$: Number of predicate/decision nodes (`if`, `while`, `for`, `&&`, `||`, `case`).
- **Target Standard**: Keep $M \le 10$ for unit testability; $M > 20$ requires immediate refactoring.

### 2.2 Robert C. Martin's Package Metric Balance
- **Instability ($I$)**:
  $$I = \frac{C_e}{C_a + C_e} \quad (0 = \text{Stable / Core}, \ 1 = \text{Unstable / Volatile})$$
- **Abstractness ($A$)**:
  $$A = \frac{N_a}{N_c} \quad (0 = \text{All Concrete}, \ 1 = \text{All Interfaces})$$
- **Normalized Distance from the Main Sequence ($D$)**:
  $$D = |A + I - 1| \quad (\text{Ideal: } D \approx 0)$$

### 2.3 Liskov Substitution Principle (LSP) Invariant
$$\text{Pre}_{\text{Subtype}} \implies \text{Pre}_{\text{Supertype}} \quad (\text{Cannot strengthen preconditions})$$
$$\text{Post}_{\text{Supertype}} \implies \text{Post}_{\text{Subtype}} \quad (\text{Cannot weaken postconditions})$$
$$\text{Inv}_{\text{Subtype}} \land \text{Inv}_{\text{Supertype}} \equiv \text{True} \quad (\text{Invariants must hold})$$

---

## 3. GoF Design Patterns Decision Matrix

```
Requirement                                                  Recommended Pattern
-------------------------------------------------------------------------------------------------
Decouple client from concrete object creation               --> Abstract Factory / Factory Method
Step-by-step assembly of complex immutable object (4+ args) --> Fluent Builder
Enforce exactly one global thread-safe instance             --> Singleton (Double-Checked Locking)
Make incompatible interfaces work together                  --> Adapter
Add dynamic behaviors to objects without subclass explosion --> Decorator
Simplify complex multi-library subsystem                    --> Facade
Control access, add caching, or enforce authorization       --> Proxy (Virtual / Protection)
Interchangeable algorithms selected at runtime              --> Strategy
Broadcast state changes to decoupled subscribers            --> Observer (EventBus / Pub-Sub)
Encapsulate requests for undo/redo and async job queues     --> Command
Manage complex object lifecycle with state-dependent logic  --> State (FSM)
Sequential filtering pipeline (Middleware / Firewalls)      --> Chain of Responsibility
Decouple domain entities from database persistence          --> Repository + Unit of Work
-------------------------------------------------------------------------------------------------
```

---

## 4. Web Protocols & API Standards Cheat Sheet

### 4.1 HTTP Verb Safety & Idempotency
| Verb | Safe? | Idempotent? | Typical Status | Purpose |
|:---|:---:|:---:|:---|:---|
| **GET** | **Yes** | **Yes** | `200 OK` | Read resource |
| **POST** | No | No | `201 Created` / `200 OK` | Create sub-resource / trigger action |
| **PUT** | No | **Yes** | `200 OK` / `204 No Content` | Complete resource replacement |
| **PATCH** | No | No* | `200 OK` | Partial resource update |
| **DELETE**| No | **Yes** | `200 OK` / `204 No Content` | Remove resource |

### 4.2 Protocol Buffer Tag & Varint Encoding
- **Tag Byte**: $\text{Tag} = (\text{Field Number} \ll 3) \mid \text{Wire Type}$
  - `Wire Type 0`: Varint (`int32`, `int64`, `bool`).
  - `Wire Type 1`: 64-bit (`fixed64`, `double`).
  - `Wire Type 2`: Length-delimited (`string`, `bytes`, embedded messages).
- **Varint MSB Rule**: MSB $= 1$ indicates more bytes follow; MSB $= 0$ indicates the final 7-bit payload byte.

---

## 5. Application Security & Cryptographic Formulas

### 5.1 OWASP Top 10 Defense Summary
1. **Broken Access Control (IDOR)**: Enforce context-bound tenant filtering: `WHERE id = $id AND tenant_id = $auth_tenant_id`.
2. **Cryptographic Failures**: TLS 1.3 in transit; AES-256-GCM / ChaCha20-Poly1305 at rest.
3. **Injection (SQL/Command)**: Parameterized prepared statements; zero raw string interpolation.
4. **Insecure Design**: Threat modeling (STRIDE); rate limits on sensitive endpoints.
5. **Security Misconfiguration**: Disable directory listing; mask debug stack traces; strict CORS.
6. **Vulnerable Components**: Automated Dependabot / Snyk dependency audits.
7. **Auth Failures**: Multi-factor authentication; Argon2id password hashing; account lockout.
8. **Integrity Failures**: Cryptographic signature validation on all serialized payloads/updates.
9. **Logging Failures**: Centralized audit trails; automated alerting on authentication spikes.
10. **SSRF**: Whitelist permitted outbound URLs; block loopback (`127.0.0.1`) and cloud metadata (`169.254.169.254`).

### 5.2 Distributed Token Bucket Rate Limiting
$$T = \min(C, T + \Delta t \cdot r)$$
- If $T \ge 1$: Allow request, decrement $T \gets T - 1$.
- If $T < 1$: Reject with HTTP `429 Too Many Requests`.
