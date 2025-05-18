# Energy-Aware Real-Time Scheduling

This project implements and compares three scheduling algorithms—**EDF**, **Static EDF**, and **Cycle-Conserving EDF (CC-EDF)**—in a custom-built Python simulator. It was developed to explore energy-efficiency tradeoffs in real-time systems under varying workloads.

Developed as part of *CPRE 558: Real-Time Systems* at Iowa State University.

---

## Objectives

- Implement a real-time scheduling simulator using EDF-based algorithms
- Evaluate task set performance under varying utilization (light, medium, heavy)
- Analyze metrics such as:
  - Total energy consumption
  - Missed deadlines
  - CPU idle time
- Demonstrate how frequency scaling (Static EDF, CC-EDF) improves energy efficiency

---

## System Overview

| Module | Description |
|--------|-------------|
| `EDF Scheduler` | Implements base EDF, Static EDF (fixed frequency scaling), and CC-EDF (dynamic slack-based scaling) |
| `Task Module` | Manages task periods, deadlines, execution times (WCET and actual) |
| `Simulation Core` | Orchestrates task execution, deadline tracking, energy logging |
| `Energy Model` | Frequency-to-power mapping used to compute energy cost |
| `Configuration` | Simulation parameters, workload definitions, GUI controls |

---

## Algorithm Summary

| Algorithm | Description | Notes |
|----------|-------------|-------|
| **EDF** | Executes tasks at max frequency to meet deadlines | Simple but energy inefficient |
| **Static EDF** | Sets CPU frequency based on task utilization | Reduces energy but assumes WCET |
| **CC-EDF** | Dynamically scales frequency based on actual task slack | Most energy efficient |

---

## Tools & Libraries

- Python 3
- `heapq`, `random`, `copy`
- `customtkinter` for GUI

---

## Project Limitations
- Simulator does not model leakage power or I/O
- WCET, frequency, and power usage are simplified for educational use
- Slack estimation in CC-EDF is heuristic-based
