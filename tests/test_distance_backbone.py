import networkx as nx
from distanceclosure import distance_backbone


def test_distance_backbone_undirected(kind: str, algorithm: str) -> None:
    G = nx.Graph()

    G.add_weighted_edges_from([
        (0, 1, 1.0),
        (1, 2, 2.0),
        (2, 3, 1.0),
        (3, 4, 2.0),
        (0, 2, 4.0),   
        (1, 3, 5.0),   
        (2, 4, 4.0)   
    ])

    B = distance_backbone(G, kind=kind, algorithm=algorithm)

    expected_edges = {
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4)
    }

    actual_edges = {edge for edge in B.edges()}

    return actual_edges == expected_edges


def test_distance_backbone_directed(kind: str, algorithm: str) -> None:
    G = nx.DiGraph()

    G.add_weighted_edges_from([
        (0, 1, 1.0),
        (1, 2, 2.0),
        (2, 3, 1.0),
        (3, 4, 2.0),
        (0, 2, 4.0),   
        (1, 3, 5.0),   
        (2, 4, 4.0),   
        (0, 4, 10.0) 
    ])

    B = distance_backbone(G, kind=kind, algorithm=algorithm)

    expected_edges = {
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),
    }

    actual_edges = {edge for edge in B.edges()}

    return actual_edges == expected_edges


possible_algorithms = {"iterative", "flagged", "closure", "heuristic"}
possible_kinds = {"metric", "ultrametric"}

for kind in possible_kinds:
    for algorithm in possible_algorithms:
        test_1 = test_distance_backbone_undirected(kind=kind, algorithm=algorithm)
        test_2 = test_distance_backbone_directed(kind=kind, algorithm=algorithm)

        print(f"Undirected : {kind} : {algorithm} : {test_1}")
        print(f"Directed : {kind} : {algorithm} : {test_2}")
