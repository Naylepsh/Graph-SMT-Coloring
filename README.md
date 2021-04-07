# Graph Coloring Solver

Generalization of [Tutors problem](https://github.com/Naylepsh/UWr-II/blob/master/Term%20V/PiZZO/ex2/zadanie%201.pdf) (pdf in Polish).
Given a json file and a number of colors on input produces vertex color assignment (if one exists) using z3solver.

## How it works

A graph is stripped of non-troublesome vertices (those whose degree is lower than a given number of colors \[n]).
Each troublesome vertex is given \[n] variables to represent its color. Each vertex gets a clause that says the vertex can have only one of those colors at the same time. Next, all the edges between those vertices get a bunch of clauses that say one's vertices cannot have the same colors. All those clauses are then forwarded to SMT solver. At the end, the leftover colors are assigned to previously removed vertices with simple DFS color assignment.

## How to run

- Install z3solver `pip install z3-solver`
- Get the repo

  ```
  git clone https://github.com/Naylepsh/Graph-SMT-Coloring.git
  cd Graph-SMT-Coloring
  ```

- Run the script with `python solve.py path/to/file.json number_of_colors`

To check out expected graph file structure refer to [sample_graph.json](https://github.com/Naylepsh/Graph-SMT-Coloring/blob/master/sample_graph.json)
