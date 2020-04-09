import json
import sys
from itertools import combinations
from copy import deepcopy


class Vertex():

    def __init__(self, id):
        self.id = id
        self.neighbours = []

    def add_neighbour(self, vertex):
        if vertex.id not in map(lambda node: node.id, self.neighbours):
            self.neighbours.append(vertex)

    def __str__(self):
        return f"""vertex id: {self.id}
    neighbours: {', '.join(map(lambda node: str(node.id), self.neighbours))}"""


class Graph():

    def __init__(self):
        self.vertices = []

    def add_vertex(self, vertex):
        if vertex.id not in map(lambda vertex: vertex.id, self.vertices):
            self.vertices.append(vertex)

    def connect_vertices(self, vertex1, vertex2):
        vertex1.add_neighbour(vertex2)
        vertex2.add_neighbour(vertex1)

    def reindex_vertices(self, vertices):
        for i, vertex in enumerate(vertices):
            vertex.id = i

    def __str__(self):
        vertices_info = []
        for node in self.vertices:
            vertices_info.append(str(node))
        return '\n'.join(vertices_info)


class ConflictsGraph(Graph):

    def __init__(self, filename):
        super().__init__()
        self.init_from_json(filename)
        self.groups = []

    def init_from_json(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            for id in range(1, data['nodes']+1):
                vertex = Vertex(id)
                self.add_vertex(vertex)
            for conflict in data['conflicts']:
                source = self.vertices[conflict['source']-1]
                self.add_vertex(source)
                disliked = self.vertices[conflict['disliked']-1]
                self.add_vertex(disliked)
                self.connect_vertices(source, disliked)

    def _remove_irrevelant_vertices(self, vertices):
        """Leaves only those vertices that can make impact on coloring (coloring of vertices of degree < #groups is irrevelant)"""
        vertices = list(filter(lambda vertex: len(
            vertex.neighbours) >= len(self.groups), vertices))
        for vertex in vertices:
            vertex.neighbours = list(
                filter(lambda v: v in vertices, vertex.neighbours))

    def _leave_relevant_subgraph(self):
        """Loops remove_irrevelant_vertices method till there are none irrevelant vertices left"""
        vertices = deepcopy(self.vertices)
        prev = len(vertices)
        self._remove_irrevelant_vertices(vertices)
        while len(vertices) != prev:
            prev = len(vertices)
            self._remove_irrevelant_vertices(vertices)
        return vertices

    def to_SAT(self):
        def group(group_id, node_id):
            return str(len(self.groups) * node_id + group_id)

        def not_group(group_id, node_id):
            return '-' + group(group_id, node_id)

        def at_least_one_group(node_id):
            return [group(group_id, node_id) for group_id in self.groups]

        def not_both_groups(node_id, group1_id, group2_id):
            return [not_group(group_id, node_id) for group_id in [group1_id, group2_id]]

        def exactly_one_group(node_id):
            return [at_least_one_group(node_id)] \
                + [not_both_groups(node_id, group1_id, group2_id)
                   for (group1_id, group2_id) in combinations(self.groups, 2)]

        def not_the_same_group(node1_id, node2_id, group_id):
            return [
                not_group(group_id, node1_id),
                not_group(group_id, node2_id)
            ]

        def not_the_same_groups(node1_id, node2_id):
            return [not_the_same_group(node1_id, node2_id, group_id) for group_id in self.groups]

        vertices = self._leave_relevant_subgraph()
        clauses = []
        visited = []
        for vertex in vertices:
            visited.append(vertex)
            clauses += exactly_one_group(vertex.id)
            for neighbour in vertex.neighbours:
                if neighbour not in visited:
                    clauses += not_the_same_groups(vertex.id, neighbour.id)

        vars_num = len(self.groups)*len(vertices)
        clauses_num = len(clauses)

        return [vertices, vars_num, clauses_num, clauses]

    def to_SAT_string(self):
        def format_clauses(clauses):
            return '\n'.join(list(map(lambda clause: ' '.join(clause+['0']), clauses)))

        *_, clauses = self.to_SAT()
        if len(clauses) == 0:
            return f'p cnf 1 1\n1 0'
        return f'p cnf {len(self.groups)*len(self.vertices)} {len(clauses)}\n' + format_clauses(clauses)

    def resolve_conflicts(self, solver, groups_num):
        self.groups = list(range(1, groups_num + 1))
        vertices, *_, clauses = self.to_SAT()
        # assigns groups to vertices with degree > #groups
        res, grouped = solver.solve(vertices, clauses)
        if res == 'UNSAT':
            return res

        # simple group assignment using DFS
        for vertex in self.vertices:
            if not vertex.id in grouped:
                available_groups = [0 for _ in len(self.groups)]
                for neighbour in vertex.neighbours:
                    if neighbour.id in grouped:
                        group = grouped[neighbour.id] - 1
                        available_groups[group] = 1
                group = available_groups.index(0) + 1
                grouped[vertex.id] = group

        return grouped

    def check_group_assignment(self, group):
        for vertex in self.vertices:
            vertex_group = group[vertex.id]
            for neighbour in vertex.neighbours:
                neighbour_group = group[neighbour.id]
                if vertex_group == neighbour_group:
                    return False
        return True
