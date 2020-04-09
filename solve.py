import sys
from conflict_graph import ConflictsGraph
from conflict_solver import ConflictsSolver

if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print(
            'Invalid number of arguments. Provide a graph filename and a number of colors')
    graph_file = sys.argv[1]
    colors_num = int(sys.argv[2])

    graph = ConflictsGraph(graph_file)
    solver = ConflictsSolver(colors_num)
    result = graph.resolve_conflicts(solver, colors_num)
    print(result)
