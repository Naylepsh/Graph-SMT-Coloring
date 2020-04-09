from conflict_graph import ConflictsGraph
import sys

if __name__ == '__main__':
    graph_file = sys.argv[1]
    graph = ConflictsGraph(graph_file)
    print(graph.to_SAT_string())
