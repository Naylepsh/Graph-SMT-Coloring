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
        self.colors = []

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
            vertex.neighbours) >= len(self.colors), vertices))
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
        def color(color_id, node_id):
            return str(len(self.colors) * node_id + color_id)

        def not_color(color_id, node_id):
            return '-' + color(color_id, node_id)

        def at_least_one_color(node_id):
            return [color(color_id, node_id) for color_id in self.colors]

        def not_both_colors(node_id, color1_id, color2_id):
            return [not_color(color_id, node_id) for color_id in [color1_id, color2_id]]

        def exactly_one_color(node_id):
            return [at_least_one_color(node_id)] \
                + [not_both_colors(node_id, color1_id, color2_id)
                   for (color1_id, color2_id) in combinations(self.colors, 2)]

        def not_the_same_color(node1_id, node2_id, color_id):
            return [
                not_color(color_id, node1_id),
                not_color(color_id, node2_id)
            ]

        def not_the_same_colors(node1_id, node2_id):
            return [not_the_same_color(node1_id, node2_id, color_id) for color_id in self.colors]

        vertices = self._leave_relevant_subgraph()
        clauses = []
        visited = []
        for vertex in vertices:
            visited.append(vertex)
            clauses += exactly_one_color(vertex.id)
            for neighbour in vertex.neighbours:
                if neighbour not in visited:
                    clauses += not_the_same_colors(vertex.id, neighbour.id)

        vars_num = len(self.colors)*len(vertices)
        clauses_num = len(clauses)

        return [vertices, vars_num, clauses_num, clauses]

    def to_SAT_string(self):
        def format_clauses(clauses):
            return '\n'.join(list(map(lambda clause: ' '.join(clause+['0']), clauses)))

        *_, clauses = self.to_SAT()
        if len(clauses) == 0:
            return f'p cnf 1 1\n1 0'
        return f'p cnf {len(self.colors)*len(self.vertices)} {len(clauses)}\n' + format_clauses(clauses)

    def resolve_conflicts(self, solver, colors_num):
        self.colors = list(range(1, colors_num + 1))
        vertices, *_, clauses = self.to_SAT()
        # assigns groups to vertices with degree > #groups
        res, colored = solver.solve(vertices, clauses)
        if res == 'UNSAT':
            return res

        # simple color assignment using DFS
        for vertex in self.vertices:
            if not vertex.id in colored:
                available_colors = [0 for _ in len(self.colors)]
                for neighbour in vertex.neighbours:
                    if neighbour.id in colored:
                        color = colored[neighbour.id] - 1
                        available_colors[color] = 1
                color = available_colors.index(0) + 1
                colored[vertex.id] = color

        return colored

    def check_color_assignment(self, colored):
        for vertex in self.vertices:
            vertex_group = colored[vertex.id]
            for neighbour in vertex.neighbours:
                neighbour_group = colored[neighbour.id]
                if vertex_group == neighbour_group:
                    return False
        return True
