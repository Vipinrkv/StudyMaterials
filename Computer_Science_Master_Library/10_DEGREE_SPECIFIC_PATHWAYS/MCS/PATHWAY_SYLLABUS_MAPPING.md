# MCS (M.Sc. Computer Science) Academic Pathway & Syllabus Mapping

**Degree Program:** Master of Science in Computer Science (MCS / M.Sc. CS)  
**Curricular Governance:** Savitribai Phule Pune University (SPPU CBCS Postgraduate Regulations)  
**Standard Duration:** 2 Years (4 Semesters)  
**Primary Library Levels:** **Level 4 (Advanced Undergraduate) through Level 8 (Master Engineer & Researcher)**, with Level 9 research modules.

---

## 1. Degree Profile & Target Outcomes
The Master of Science in Computer Science program is a rigorous postgraduate degree emphasizing advanced computational theory, mathematical algorithm analysis, operating system kernel internals, distributed consensus, deep learning theory, and original research methodology. Graduates pursue advanced careers as Principal Systems Engineers, Research Scientists, or Ph.D. scholars.

---

## 2. Semester-by-Semester Curriculum Mapping

### Year 1: Advanced Systems, Algorithm Analysis & Machine Learning

#### Semester I
- **CS-101: Design and Analysis of Algorithms (DAA)**
  - *Library Alignment:* [Level 3: CH07](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/03_LEVEL_3_INTERMEDIATE_CS/CH07_ASYMPTOTIC_ANALYSIS_COMPLEXITY/README.md), [Level 4: CH06](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/04_LEVEL_4_ADVANCED_UNDERGRADUATE/CH06_INTERMEDIATE_REPRESENTATION_SSA/README.md), [Level 6: CH08](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/CH08_ALGORITHMIC_COMPLEXITY_NP/README.md)
  - *Topics Covered:* Amortized analysis (potential method), Master's theorem, dynamic programming, network flow (Ford-Fulkerson, Edmonds-Karp), NP-completeness and reductions (3-SAT to CLIQUE/VERTEX-COVER).
  - *Laboratory Practicum:* [ch08_sat_solver_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/LABS/ch08_sat_solver_lab.py).
- **CS-102: Advanced Operating Systems & Kernel Architecture**
  - *Library Alignment:* [Level 4: CH01](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/04_LEVEL_4_ADVANCED_UNDERGRADUATE/CH01_OPERATING_SYSTEM_CONCEPTS/README.md), [CH02](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/04_LEVEL_4_ADVANCED_UNDERGRADUATE/CH02_PROCESSES_THREADS_CONCURRENCY/README.md), [CH03](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/04_LEVEL_4_ADVANCED_UNDERGRADUATE/CH03_VIRTUAL_MEMORY_AND_PAGING/README.md), [Level 6: CH05](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/CH05_LINUX_KERNEL_INTERNALS/README.md)
  - *Topics Covered:* Virtual memory page tables, TLB shootdown, Completely Fair Scheduler (CFS), eBPF tracepoints, Linux namespaces and cgroups, lockless ring buffers.
  - *Laboratory Practicum:* [ch05_ebpf_kernel_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/LABS/ch05_ebpf_kernel_lab.py).
- **CS-103: Advanced Database Systems (Distributed & NoSQL)**
  - *Library Alignment:* [Level 4: CH07](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/04_LEVEL_4_ADVANCED_UNDERGRADUATE/CH07_TRANSACTION_PROCESSING_ACID/README.md), [Level 6: CH02](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/CH02_DISTRIBUTED_TRANSACTIONS_2PC/README.md)
  - *Topics Covered:* Strict 2PL, MVCC snapshot isolation, Write-skew anomaly, ARIES recovery, Distributed 2PC, Consistent Hashing.
  - *Laboratory Practicum:* [ch02_2pc_coordinator_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/LABS/ch02_2pc_coordinator_lab.py).

#### Semester II
- **CS-201: Distributed Computing & Consensus Protocols**
  - *Library Alignment:* [Level 4: CH08](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/04_LEVEL_4_ADVANCED_UNDERGRADUATE/CH08_DISTRIBUTED_SYSTEM_FOUNDATIONS/README.md), [Level 6: CH01](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/CH01_ADVANCED_DISTRIBUTED_CONSENSUS/README.md), [Level 8: CH01](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/CH01_DISTRIBUTED_CONSENSUS_RESEARCH/README.md)
  - *Topics Covered:* Lamport timestamps, Vector clocks, Raft consensus algorithm, Multi-Paxos, Byzantine Fault Tolerance (PBFT), Google Spanner TrueTime commit-wait.
  - *Laboratory Practicum:* [ch01_raft_consensus_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/LABS/ch01_raft_consensus_lab.py), [ch01_raft_membership_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/LABS/ch01_raft_membership_lab.py).
- **CS-202: Artificial Intelligence & Deep Learning Foundations**
  - *Library Alignment:* [Level 6: CH06](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/CH06_DEEP_LEARNING_MATHEMATICAL_FOUNDATIONS/README.md), [CH07](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/CH07_DISTRIBUTED_ML_TRAINING_INFERENCE/README.md)
  - *Topics Covered:* Computational graphs, reverse-mode autodiff matrix calculus, transformer self-attention mechanisms, loss landscapes, distributed data/tensor parallelism.
  - *Laboratory Practicum:* [ch06_backprop_autograd_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/LABS/ch06_backprop_autograd_lab.py).
- **Year 1 Capstone Project:** [NexusEngine Distributed Streaming Engine](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/LEVEL_6_CAPSTONE_PROJECT.md).

---

### Year 2: Research Methods, Formal Verification & Masters Dissertation

#### Semester III
- **CS-301: Formal Methods & Program Verification**
  - *Library Alignment:* [Level 8: CH02](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/CH02_FORMAL_METHODS_VERIFICATION/README.md), [Level 9: CH01](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/09_LEVEL_9_VETERAN_EXPERT/CH01_ADVANCED_TYPE_THEORY/README.md)
  - *Topics Covered:* Hoare logic, loop invariants, operational semantics, model checking, TLA+ state-space exploration, Curry-Howard correspondence, linear types.
  - *Laboratory Practicum:* [ch02_hoare_model_checking_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/LABS/ch02_hoare_model_checking_lab.py), [ch01_linear_types_borrow_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/09_LEVEL_9_VETERAN_EXPERT/LABS/ch01_linear_types_borrow_lab.py).
- **CS-302: Advanced Cryptography & Information Security**
  - *Library Alignment:* [Level 8: CH08](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/CH08_QUANTUM_RESISTANT_CRYPTO/README.md), [Level 9: CH04](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/09_LEVEL_9_VETERAN_EXPERT/CH04_ZERO_KNOWLEDGE_PROOF_SYSTEMS/README.md)
  - *Topics Covered:* Post-quantum lattice cryptography (ML-KEM / Kyber), zero-knowledge proofs, arithmetic circuits to R1CS, QAP, Schwartz-Zippel lemma.
  - *Laboratory Practicum:* [ch04_r1cs_zkp_verifier_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/09_LEVEL_9_VETERAN_EXPERT/LABS/ch04_r1cs_zkp_verifier_lab.py).

#### Semester IV
- **CS-401: Full-Time Industrial Research Internship / Master's Dissertation**
  - *Library Alignment:* [Level 8: CH09](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/CH09_RESEARCH_METHODOLOGY_CS/README.md), [Level 9: CH10](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/09_LEVEL_9_VETERAN_EXPERT/CH10_DISSERTATION_AND_DEFENSE/README.md)
  - *Focus:* Original research thesis, scientific publication, empirical benchmarking harness, and public dissertation defense.
  - *Laboratory Practicum:* [ch10_dissertation_eval_harness_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/09_LEVEL_9_VETERAN_EXPERT/LABS/ch10_dissertation_eval_harness_lab.py).
- **Postgraduate Capstone Benchmark:** [Aethelgard Heterogeneous Runtime](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/LEVEL_8_CAPSTONE_PROJECT.md) or [Project OLYMPUS](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/09_LEVEL_9_VETERAN_EXPERT/LEVEL_9_CAPSTONE_PROJECT.md).

---

## 3. Examination & Interview Milestones
- **Comprehensive Postgraduate Examination Preparation:** Practice with [UNIVERSITY_EXAM_CORE_CS_AND_SYSTEMS_PAPER_WITH_SOLUTIONS.md](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/15_EXAMINATIONS_AND_QUESTION_BANK/UNIVERSITY_EXAM_CORE_CS_AND_SYSTEMS_PAPER_WITH_SOLUTIONS.md) and [UNIVERSITY_EXAM_ADVANCED_ENGINEERING_AND_RESEARCH_PAPER_WITH_SOLUTIONS.md](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/15_EXAMINATIONS_AND_QUESTION_BANK/UNIVERSITY_EXAM_ADVANCED_ENGINEERING_AND_RESEARCH_PAPER_WITH_SOLUTIONS.md).
- **Senior Technical & Research Scientist Interviews:** Rigorous mastery of [CATEGORY_C_EXPERIENCED_INTERVIEWS.md](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/14_INTERVIEW_PREPARATION/CATEGORY_C_EXPERIENCED_INTERVIEWS.md) and [CATEGORY_D_PRINCIPAL_ARCHITECT_INTERVIEWS.md](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/14_INTERVIEW_PREPARATION/CATEGORY_D_PRINCIPAL_ARCHITECT_INTERVIEWS.md).
