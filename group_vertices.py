import sys
from conflict_graph import ConflictsGraph
from solver import ConflictsSolver

if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print('Invalid number of arguments. Provide graph filename and number of groups to group by.')
    graph_file = sys.argv[1]
    groups_num = int(sys.argv[2])

    graph = ConflictsGraph(graph_file)
    solver = ConflictsSolver(groups_num)
    result = graph.resolve_conflicts(solver, groups_num)
    print(result)
