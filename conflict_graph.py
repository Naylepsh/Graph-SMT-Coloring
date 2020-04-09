import json
import sys
from itertools import combinations


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

    def reindex_vertices(self):
        for i, vertex in enumerate(self.vertices):
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

    def init_from_json(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            self.groups = list(range(1, data['groups'] + 1))
            for id in range(1, data['nodes']+1):
                vertex = Vertex(id)
                self.add_vertex(vertex)
            for conflict in data['conflicts']:
                whiner = self.vertices[conflict['source']-1]
                self.add_vertex(whiner)
                victim = self.vertices[conflict['disliked']-1]
                self.add_vertex(victim)
                self.connect_vertices(whiner, victim)

    def _remove_irrevelant_vertices(self):
        """Leaves only those vertices that can make impact on coloring (coloring of vertices of degree < #groups is irrevelant)"""
        self.vertices = list(filter(lambda vertex: len(
            vertex.neighbours) >= len(self.groups), self.vertices))
        for vertex in self.vertices:
            vertex.neighbours = list(
                filter(lambda v: v in self.vertices, vertex.neighbours))
        self.reindex_vertices()

    def _leave_relevant_subgraph(self):
        """Loops remove_irrevelant_vertices method till there are none irrevelant vertices left"""
        prev = len(self.vertices)
        self._remove_irrevelant_vertices()
        while len(self.vertices) != prev:
            prev = len(self.vertices)
            self._remove_irrevelant_vertices()

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

        self._leave_relevant_subgraph()
        clauses = []
        visited = []
        for vertex in self.vertices:
            visited.append(vertex)
            clauses += exactly_one_group(vertex.id)
            for neighbour in vertex.neighbours:
                if neighbour not in visited:
                    clauses += not_the_same_groups(vertex.id, neighbour.id)

        vars_num = len(self.groups)*len(self.vertices)
        clauses_num = len(clauses)

        return [vars_num, clauses_num, clauses]

    def to_SAT_string(self):
        def format_clauses(clauses):
            return '\n'.join(list(map(lambda clause: ' '.join(clause+['0']), clauses)))

        *_, clauses = self.to_SAT()
        if len(clauses) == 0:
            return f'p cnf 1 1\n1 0'
        return f'p cnf {len(self.groups)*len(self.vertices)} {len(clauses)}\n' + format_clauses(clauses)
