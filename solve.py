import sys
from graph import ColoredGraph
from colors_solver import ColorsSolver

if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print(
            'Invalid number of arguments. Provide a graph filename and a number of colors')
    graph_file = sys.argv[1]
    colors_num = int(sys.argv[2])

    graph = ColoredGraph(graph_file)
    solver = ColorsSolver(colors_num)
    result = graph.resolve_colors(solver, colors_num)
    print(result)
