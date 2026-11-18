# LEVEL 2 CAPSTONE PROJECT: INDUSTRIAL EMBEDDED KEY-VALUE STORAGE ENGINE (MiniKVS)

---

## 1. Project Title & Overview
**Project Title:** MiniKVS — Industrial Embedded Key-Value Storage & Persistent Log Engine  
**Difficulty:** Level 2 (Systems Programming Foundation Capstone)  
**Target Qualifications:** BCS, BCA, MCS, MCA, BESE, MESE, B.Tech SE, M.Tech SE  
**Primary Languages:** C99/C11 (Engine Source) & Python 3.11+ (Verification Harness)  

This capstone project synthesizes all ten foundational subjects mastered in Level 2 into a high-performance, embedded storage engine modeled after Bitcask (the storage engine behind Riak) and Redis. Students build a fully functioning key-value store that combines an in-memory hash table with an append-only binary disk log, providing instantaneous $\mathcal{O}(1)$ key lookups through direct byte-offset random access seeking.

---

## 2. Integrative Concept Mapping (Level 2 Subjects)

| Chapter | MiniKVS Architectural Component |
|:---|:---|
| **CH01: Mental Models & Problem Solving** | Algorithmic state transitions, finite state machine query parsing, invariant enforcement. |
| **CH02: C Fundamentals & Types** | Bit-level integer encodings, fixed-width types (`uint32_t`, `uint64_t`), Little-Endian serialization. |
| **CH03: Operators & Control Flow** | Hash computation bitwise shifts (`>>`, `<<`, `^`), error-branching state machines. |
| **CH04: Functions & Call Stack** | Modular API design (`kvs_open`, `kvs_put`, `kvs_get`, `kvs_delete`, `kvs_close`), reentrant execution. |
| **CH05: Arrays, Strings & Pointers** | Pointer arithmetic, contiguous array flattening, safe string manipulation without buffer overruns. |
| **CH06: Structs, Unions & Memory Alignment** | Packed wire format (`#pragma pack(1)`), natural alignment of in-memory metadata structs. |
| **CH07: Dynamic Memory & Heap Management** | Dynamic bucket resizing with geometric expansion ($\times 2$), tracked memory allocation. |
| **CH08: File I/O, Streams & Persistence** | Binary append logging (`"ab"`), random-access record lookup via `fseek` (`SEEK_SET`) and `fread`. |
| **CH09: Preprocessor & Build Systems** | Modular header architecture (`mini_kvs.h`), include guards, macro safety (`do-while(0)`). |
| **CH10: Defensive Programming & Debugging** | Design by contract assertions, boundary checking, shadow memory emulation, zero-leak verification. |

---

## 3. Storage Architecture Specification (The Bitcask Pattern)

```
IN-MEMORY COMPONENT (RAM)
+-------------------------------------------------------------------------+
| Hash Table Index (Keydir)                                               |
| Key "user:101"  --> [ File Offset: 0x00000000 | Value Size: 48 bytes ]   |
| Key "user:102"  --> [ File Offset: 0x00000048 | Value Size: 64 bytes ]   |
+-------------------------------------------------------------------------+
                               |
                               | Direct Random-Access Disk Seek (fseek)
                               v
ON-DISK COMPONENT (Non-Volatile Storage: database.kvs)
+-------------------------------------------------------------------------+
| [ Record 0 ] Magic: 0x5A | Timestamp | KeyLen | ValLen | Key | Val | CRC |
+-------------------------------------------------------------------------+
| [ Record 1 ] Magic: 0x5A | Timestamp | KeyLen | ValLen | Key | Val | CRC |
+-------------------------------------------------------------------------+
| [ Record 2 (Tombstone) ] Deleted Flag = 1                              |
+-------------------------------------------------------------------------+
```

### Record Header Wire Format (`#pragma pack(1)`)
```
[ Magic Byte (1B: 0x5A) ][ Flags (1B) ][ Timestamp (8B) ][ KeyLen (2B) ][ ValLen (4B) ]
Total Fixed Header = 16 bytes, followed by Key Payload, Value Payload, and 1-byte Checksum.
```

---

## 4. Key Performance Characteristics
1. **Append-Only Sequential Writes**: High-throughput $\mathcal{O}(1)$ sequential disk writes without requiring disk head repositioning.
2. **Instant Random Lookups**: By indexing file offsets in RAM, retrieving any value requires exactly **one single disk seek** ($\mathcal{O}(1)$ disk I/O).
3. **Crash Resilience**: All writes append full records with checksums; incomplete records caused by sudden power cuts are easily identified and discarded upon recovery.

---

## 5. Source Code & Test Harness Deliverables

- **C Engine Implementation**: [`13_PROJECTS/level_2_capstone/mini_kvs.c`](mini_kvs.c)
- **C Header Specification**: [`13_PROJECTS/level_2_capstone/mini_kvs.h`](mini_kvs.h)
- **Automated Verification Harness**: [`13_PROJECTS/level_2_capstone/mini_kvs_verifier.py`](mini_kvs_verifier.py)

---

## 6. Verification & Audit Procedure

1. Run the Python automated test harness:
   ```bash
   python Computer_Science_Master_Library/13_PROJECTS/level_2_capstone/mini_kvs_verifier.py
   ```
2. Verify:
   - Insertion (`PUT`), retrieval (`GET`), update, and deletion (`DELETE` tombstones).
   - Binary record serialization and byte-exact checksum validation.
   - Persistence recovery: reopening an existing file rebuilds the in-memory index automatically.
   - Memory leak tracking: all allocated memory is balanced back to 0 bytes on shutdown.
   - All assertions pass with exit code 0.
