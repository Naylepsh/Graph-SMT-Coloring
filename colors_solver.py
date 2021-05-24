from z3 import Solver, sat, Not, Or, Bool


class ColorsSolver:
    def __init__(self, colors_num):
        self.solver = Solver()
        self.vars = {}
        self.colors_num = colors_num

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
            for i in range(self.colors_num):
                key = str(vertex.id*self.colors_num + i + 1)
                self.vars[key] = Bool(key)

    def _assign_colors(self):
        def chunks(array, size):
            for i in range(0, len(array), size):
                yield i // size, array[i:i + size]

        def literal_var(literal):
            return abs(int(literal))

        model = self.solver.model()
        keys = sorted(list(self.vars.keys()), key=literal_var)

        colored = {}
        for _, chunk in chunks(keys, self.colors_num):
            values = list(
                map(lambda key: model.evaluate(self.vars[key]), chunk))
            group = values.index(True) + 1
            key = int(chunk[0]) // self.colors_num
            colored[key] = group
        return colored

    def _get_model(self):
        return self._assign_colors()

    def solve(self, vertices, clauses):
        self._create_vars(vertices)
        self._add_clauses(clauses)

        if self.solver.check() == sat:
            return ['SAT', self._get_model()]
        else:
            return ['UNSAT', None]
