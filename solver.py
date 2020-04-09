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
            return Not(self._access_var(literal_id))
        literal_id = literal
        return self._access_var(literal_id)

    def _is_negated_literal(self, literal):
        return literal[0] == '-'

    def _access_var(self, literal_id):
        key = str(literal_id)
        return self.vars[key]

    def _create_vars(self, vertices):
        for vertex in vertices:
            for i in range(self.groups_num):
                key = str(vertex.id*self.groups_num + i + 1)
                self.vars[key] = Bool(key)

    def _assign_groups(self):
        def chunks(array, size):
            for i in range(0, len(array), size):
                yield i // size, array[i:i + size]

        def literal_var(literal):
            return abs(int(literal))

        model = self.solver.model()
        keys = sorted(list(self.vars.keys()), key=literal_var)

        for _, chunk in chunks(keys, self.groups_num):
            values = list(
                map(lambda key: model.evaluate(self.vars[key]), chunk))
            group = values.index(True)
            print(int(chunk[0]) // self.groups_num, group)

    def _print_model(self):
        self._assign_groups()

    def solve(self, vertices, clauses):
        self._create_vars(vertices)
        self._add_clauses(clauses)

        if self.solver.check() == sat:
            print("SAT")
            self._print_model()
        else:
            print("UNSAT")


if __name__ == '__main__':
    graph_file = sys.argv[1]
    groups_num = 5
    graph = ConflictsGraph(graph_file, groups_num)
    vertices, *_, clauses = graph.to_SAT()
    solver = ConflictsSolver(groups_num)
    solver.solve(vertices, clauses)

    # print(graph.to_SAT_string())
