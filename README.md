# 🧩 Sudoku CSP Solver

A high-performance Sudoku solver implemented as a **Constraint Satisfaction Problem (CSP)**. This tool visualizes how different AI algorithms—ranging from basic Backtracking to advanced Arc Consistency (AC-3)—tackle puzzles of varying difficulty.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-blue?style=for-the-badge)

---

## 🚀 Features

* **Real-time Visualization:** Watch the algorithm "think" as it fills and backtracks through cells.
* **Multiple Solving Strategies:**
    * **Backtracking (BT):** The foundational depth-first search.
    * **Forward Checking (FC):** Prunes domains of neighbors to fail faster.
    * **AC-3 (Arc Consistency):** Pre-processing and during-search constraint propagation.
    * **MRV Heuristic:** Uses "Minimum Remaining Values" to choose the most constrained variable next.
* **Difficulty Presets:** Test against Easy, Medium, Hard, and "Very Hard" benchmarks.
* **Performance Metrics:** Tracks execution time and the number of nodes explored.

---

## 🛠️ Tech Stack

- **Language:** Python 3.x
- **GUI Framework:** Tkinter
- **Algorithms:** Constraint Satisfaction Problem (CSP), Backtracking, AC-3, Forward Checking.

---
## Output
<img width="743" height="774" alt="Screenshot 2026-04-15 213523" src="https://github.com/user-attachments/assets/1f64db2b-f729-4bcb-a05b-50fed708a964" />

## 🧠 How it Works (The CSP Approach)

This solver treats Sudoku as a CSP where:
- **Variables ($X$):** The 81 cells on the grid.
- **Domains ($D$):** Integers $\{1, 2, \dots, 9\}$ for each cell.
- **Constraints ($C$):** - **Row Constraint:** Every digit must be unique in a row.
    - **Column Constraint:** Every digit must be unique in a column.
    - **Box Constraint:** Every digit must be unique in each $3 \times 3$ sub-grid.

### Included Algorithms:
1. **AC-3 Algorithm:** Reduces the search space by ensuring every variable is arc-consistent with its neighbors.
2. **Backtracking Search:** A recursive DFS that tries assignments and reverts when it hits a dead end.
3. **Forward Checking:** A local consistency check that looks ahead to ensure the current move doesn't leave future cells with zero valid options.

---

## 💻 Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/sudoku-csp-solver.git](https://github.com/your-username/sudoku-csp-solver.git)
   cd sudoku-csp-solver
