from conflict_graph import ConflictsGraph
import sys
from z3 import Solver, sat, Not, Or, Bool


class ConflictsSolver:
    def __init__(self, groups_num):
        self.solver = Solver()
        self.vars = {}
        self.groups_num = groups_num

    def _add_clauses(self, clauses):
        for clause in self._parse_clauses(clauses):
            self.solver.add(clause)

    def _parse_clauses(self, clauses):
        for clause in clauses:
            yield self._parse_clause(clause)

    def _parse_clause(self, clause):
        return Or([self._parse_literal(literal) for literal in clause])

    def _parse_literal(self, literal):
        if self._is_negated_literal(literal):
            literal_id = literal[1:]
            return Not(self.vars[literal_id])
        literal_id = literal
        return self.vars[literal_id]

    def _is_negated_literal(self, literal):
        return literal[0] == '-'

    def _create_vars(self, vars_num):
        for i in range(1, vars_num + 1):
            key = str(i)
            self.vars[key] = Bool(key)

    def _assign_groups(self):
        def chunks(array, size):
            for i in range(0, len(array), size):
                yield i // size, array[i:i + size]

        model = self.solver.model()
        for i, chunk in chunks(list(self.vars.keys()), self.groups_num):
            values = list(
                map(lambda key: model.evaluate(self.vars[key]), chunk))
            group = values.index(True)
            print(i, group)

    def _print_model(self):
        self._assign_groups()
        # model = self.solver.model()
        # for key in self.vars:
        #     print(model.evaluate(self.vars[key]))

    def solve(self, vars_num, clauses):
        self._create_vars(vars_num)
        self._add_clauses(clauses)

        if self.solver.check() == sat:
            print("SAT")
            self._print_model()
        else:
            print("UNSAT")


if __name__ == '__main__':
    graph_file = sys.argv[1]
    graph = ConflictsGraph(graph_file)
    vars_num, _, clauses = graph.to_SAT()
    solver = ConflictsSolver(5)
    solver.solve(vars_num, clauses)

    # print(graph.to_SAT_string())
