# M.Tech Software Engineering / CSE Academic Pathway & Syllabus Mapping

**Degree Program:** Master of Technology in Software Engineering (M.Tech SE / CSE)  
**Curricular Governance:** AICTE Postgraduate Engineering Guidelines & SPPU M.Tech Curriculum  
**Standard Duration:** 2 Years (4 Semesters)  
**Primary Library Levels:** **Level 6 (Postgraduate Advanced) through Level 8 (Master Engineer & Researcher)**, with Level 9 cutting-edge research modules.

---

## 1. Degree Profile & Graduate Attributes
The Master of Technology in Software Engineering curriculum prepares advanced systems architects, research engineers, and technical leaders. Students gain deep theoretical and hands-on mastery over distributed consensus algorithms, high-throughput kernel runtimes, formal software verification, neural network runtime optimization, and rigorous research methodologies.

---

## 2. Semester-by-Semester Curriculum Mapping

### Year 1: Advanced Distributed Systems, Kernel Internals & Formal Methods

#### Semester I
- **MTSE-101: Advanced Distributed Systems & Consensus Architecture**
  - *Library Alignment:* [Level 6: CH01](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/CH01_ADVANCED_DISTRIBUTED_CONSENSUS/README.md), [CH02](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/CH02_DISTRIBUTED_TRANSACTIONS_2PC/README.md), [Level 8: CH01](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/CH01_DISTRIBUTED_CONSENSUS_RESEARCH/README.md)
  - *Topics Covered:* Raft linearizability, Multi-Paxos log hole recovery, 2PC over Paxos, Calvin deterministic sequencing, Google Spanner TrueTime commit-wait.
  - *Laboratory Practicum:* [ch01_raft_consensus_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/LABS/ch01_raft_consensus_lab.py), [ch01_raft_membership_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/LABS/ch01_raft_membership_lab.py).
- **MTSE-102: High-Performance Systems & Linux Kernel Architecture**
  - *Library Alignment:* [Level 6: CH03](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/CH03_HIGH_PERFORMANCE_CONCURRENCY/README.md), [CH04](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/CH04_ADVANCED_NETWORKING_IO_URING/README.md), [CH05](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/CH05_LINUX_KERNEL_INTERNALS/README.md)
  - *Topics Covered:* Lock-free data structures (Michael-Scott queue), hazard pointers, false sharing, `epoll` vs `io_uring` ring buffers, eBPF tracepoints.
  - *Laboratory Practicum:* [ch03_lockfree_queue_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/LABS/ch03_lockfree_queue_lab.py), [ch04_iouring_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/LABS/ch04_iouring_lab.py).

#### Semester II
- **MTSE-201: Formal Verification & Safety-Critical Systems**
  - *Library Alignment:* [Level 8: CH02](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/CH02_FORMAL_METHODS_VERIFICATION/README.md), [Level 9: CH01](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/09_LEVEL_9_VETERAN_EXPERT/CH01_ADVANCED_TYPE_THEORY/README.md)
  - *Topics Covered:* Hoare logic, loop invariants, operational semantics, model checking, TLA+ temporal logic, Linear type systems and Polonius borrow checker.
  - *Laboratory Practicum:* [ch02_hoare_model_checking_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/LABS/ch02_hoare_model_checking_lab.py), [ch01_linear_types_borrow_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/09_LEVEL_9_VETERAN_EXPERT/LABS/ch01_linear_types_borrow_lab.py).
- **MTSE-202: Deep Learning Runtimes & Distributed AI Systems**
  - *Library Alignment:* [Level 6: CH06](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/CH06_DEEP_LEARNING_MATHEMATICAL_FOUNDATIONS/README.md), [CH07](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/CH07_DISTRIBUTED_ML_TRAINING_INFERENCE/README.md), [Level 8: CH05](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/CH05_AI_SYSTEMS_MLOPS_INFRA/README.md)
  - *Topics Covered:* Computational graph execution, autodiff backpropagation, tensor parallelism, pipeline parallelism, FlashAttention memory optimizations.
  - *Laboratory Practicum:* [ch06_backprop_autograd_lab.py](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/LABS/ch06_backprop_autograd_lab.py).
- **Year 1 Capstone Project:** [NexusEngine Distributed Streaming Engine](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/06_LEVEL_6_POSTGRADUATE_ADVANCED/LEVEL_6_CAPSTONE_PROJECT.md).

---

### Year 2: Research Seminar & M.Tech Dissertation

#### Semester III
- **MTSE-301: Empirical Software Engineering & Research Methodology**
  - *Library Alignment:* [Level 8: CH09](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/CH09_RESEARCH_METHODOLOGY_CS/README.md), [Level 9: CH10](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/09_LEVEL_9_VETERAN_EXPERT/CH10_DISSERTATION_AND_DEFENSE/README.md)
  - *Topics Covered:* Empirical research design, hypothesis formulation, statistical hypothesis testing (t-test, ANOVA, Mann-Whitney U), academic writing.
- **MTSE-302: Dissertation Stage I (Problem Formulation & Literature Review)**
  - *Focus:* Comprehensive literature survey, systematic mapping study, prototype implementation.

#### Semester IV
- **MTSE-401: Dissertation Stage II & Master's Defense**
  - *Library Alignment:* [Level 8: LEVEL_8_CAPSTONE_PROJECT.md](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/LEVEL_8_CAPSTONE_PROJECT.md), [Level 9: LEVEL_9_CAPSTONE_PROJECT.md](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/09_LEVEL_9_VETERAN_EXPERT/LEVEL_9_CAPSTONE_PROJECT.md)
  - *Focus:* Empirical validation, rigorous benchmarking against baseline engines, formal dissertation writing, and defense before examination committee.
  - *Capstone Benchmark:* [Aethelgard Heterogeneous Runtime](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/08_LEVEL_8_RESEARCH_AND_INNOVATION/LEVEL_8_CAPSTONE_PROJECT.md) or [Project OLYMPUS Distributed Engine](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/09_LEVEL_9_VETERAN_EXPERT/LEVEL_9_CAPSTONE_PROJECT.md).

---

## 3. Examination & Interview Milestones
- **Comprehensive Postgraduate Examination Preparation:** Practice with [UNIVERSITY_EXAM_ADVANCED_ENGINEERING_AND_RESEARCH_PAPER_WITH_SOLUTIONS.md](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/15_EXAMINATIONS_AND_QUESTION_BANK/UNIVERSITY_EXAM_ADVANCED_ENGINEERING_AND_RESEARCH_PAPER_WITH_SOLUTIONS.md).
- **Staff / Principal Architect Interviews:** Rigorous mastery of [CATEGORY_C_EXPERIENCED_INTERVIEWS.md](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/14_INTERVIEW_PREPARATION/CATEGORY_C_EXPERIENCED_INTERVIEWS.md) and [CATEGORY_D_PRINCIPAL_ARCHITECT_INTERVIEWS.md](file:///c:/Users/Vipin/OneDrive/Desktop/Study/Study/Computer_Science_Master_Library/14_INTERVIEW_PREPARATION/CATEGORY_D_PRINCIPAL_ARCHITECT_INTERVIEWS.md).
