# -*- coding: utf-8 -*-
"""
Distance Backbone
=================

Compute the distance backbones of both directed and undirected weighted graphs.
"""
import numpy as np
import networkx as nx

from distanceclosure.dijkstra import single_source_target_dijkstra_path, single_source_neighbors_dijkstra_path_length
from distanceclosure.closure import distance_closure

from itertools import product
from typing import Callable


__all__ = [
    "distance_backbone",
    "metric_backbone",
    "ultrametric_backbone" 
]


def distance_backbone(D: nx.Graph | nx.DiGraph, weight: str = "weight", kind: str = "metric", algorithm: str = "iterative", distortion: bool = False, self_loops: bool = False, cutoff: int = None, verbose: bool = False) -> nx.Graph | nx.DiGraph | tuple[nx.Graph | nx.DiGraph, dict]:
    """
    Compute the distance backbone of a weighted graph.

    Parameters
    ----------
    D : Directed or undirected NetworkX graph
        A weighted distance graph.
    weight : str, optional
        Edge property containing distance values, ``weight="weight"`` by default.
    kind : {"metric", "ultrametric"}, optional
        Distance metric used to compute the backbone. "metric" compares sums while "ultrametric" compares maximums, ``kind="metric"`` by default.
    algorithm : {"iterative", "flagged", "closure", "heuristic", "approximate"}, optional
        Algorithm used to compute the backbone, ``algorithm="iterative"`` by default.
    distortion : bool, optional
        Whether to compute and return the edge distortions of edges not in the backbone, ``distortion=False`` by default.
    self_loops : bool, optional
        Whether to remove self-loops that have a shorter path back to the same node, ``self_loops=False`` by default.
    cutoff : int, optional
        Set the maximum number of connections to be searched per path, ``cutoff=None`` by default.
    verbose : bool, optional
        Whether to display computation progress, ``verbose=False`` by default.

    Returns
    -------
    nx.Graph or nx.DiGraph
        The distance backbone.
    tuple of (nx.Graph or nx.DiGraph, dict)
        Edge distortions, returned with the backbone when ``distortion=True``.

    Raises
    ------
    ValueError
        If ``kind`` or ``algorithm`` is invalid.
    """

    try:
        disjunction = _KINDS[kind]
    except KeyError:
        raise ValueError("Invalid input. Valid arguments are: {valid_kinds}".format(valid_kinds=_KINDS.keys())) from None

    try:
        chosen_algorithm = _BACKBONE_ALGORITHMS[algorithm]
    except KeyError:
        raise ValueError("Invalid input. Valid arguments are: {valid_algorithms}".format(valid_algorithms=_BACKBONE_ALGORITHMS.keys())) from None

    if chosen_algorithm is _BACKBONE_ALGORITHMS["closure"]:
        return chosen_algorithm(D, weight=weight, kind=kind, disjunction=disjunction, distortion=distortion, self_loops=self_loops, cutoff=cutoff, verbose=verbose)
    
    return chosen_algorithm(D, weight=weight, disjunction=disjunction, distortion=distortion, self_loops=self_loops, cutoff=cutoff, verbose=verbose)


def metric_backbone(D: nx.Graph | nx.DiGraph, weight: str = "weight", distortion: bool = False, self_loops: bool = False, cutoff: int = None, verbose: bool = False) -> nx.Graph | nx.DiGraph | tuple[nx.Graph | nx.DiGraph, dict]:
    """
    Compute the metric backbone of a weighted graph.

    Wrapper for :func:`distance_backbone`
    where ``kind="metric"`` and ``algorithm="iterative"``.
    """

    return distance_backbone(D, weight=weight, algorithm="iterative", kind="metric", distortion=distortion, self_loops=self_loops, cutoff=cutoff, verbose=verbose)


def ultrametric_backbone(D: nx.Graph | nx.DiGraph, weight: str = "weight", distortion: bool = False, self_loops: bool = False, cutoff: int = None, verbose: bool = False) -> nx.Graph | nx.DiGraph | tuple[nx.Graph | nx.DiGraph, dict]:
    """
    Compute the ultrametric backbone of a weighted graph.

    Wrapper for :func:`distance_backbone`
    where ``kind="ultrametric"`` and ``algorithm="iterative"``.
    """

    return distance_backbone(D, weight=weight, algorithm="iterative", kind="ultrametric", distortion=distortion, self_loops=self_loops, cutoff=cutoff, verbose=verbose)


def _flagged_backbone(D: nx.Graph | nx.DiGraph, weight: str, disjunction: Callable, distortion: bool, self_loops: bool, cutoff: int, verbose: bool) -> nx.Graph | nx.DiGraph | tuple[nx.Graph | nx.DiGraph, dict]:
    """
    Compute the distance backbone using the flagged algorithm.

    For each node in a weighted graph, use Dijkstra's algorithm to find the shortest path to each neighbor. 
    If the direct edge is not the shortest path, remove it. Otherwise, flag it as a backbone edge. 
    Stop once all remaining edges have been flagged.

    Parameters
    ----------
    D : Directed or undirected NetworkX graph
        A weighted distance graph.
    weight : str
        Edge property containing distance values.
    disjunction : Callable
        Function used to measure path distance.
    distortion : bool
        Whether to compute and return the edge distortions of edges not in the backbone.
    self_loops : bool
        Whether to remove self-loops that have a shorter path back to the same node.
    cutoff : int
        Maximum number of connections to be searched per path.
    verbose : bool
        Whether to display computation progress.

    Returns
    -------
    nx.Graph or nx.DiGraph
        The distance backbone.
    tuple of (nx.Graph or nx.DiGraph, dict)
        Edge distortions, returned with the backbone when ``distortion=True``.
    """

    G = D.copy()
    B = nx.DiGraph() if nx.is_directed(G) else nx.Graph()

    if verbose: 
        total = G.number_of_nodes()
        i = 0

    for node in list(G.nodes()):
        shortest_paths_to_neighbors = single_source_neighbors_dijkstra_path_length(G, source=node, weight=weight, disjunction=disjunction, cutoff=cutoff)

        for neighbor in list(G.neighbors(node)):
            shortest_path = shortest_paths_to_neighbors[neighbor]
            direct_path = G[node][neighbor][weight]

            if shortest_path < direct_path:
                G.remove_edge(node, neighbor)
            else:
                B.add_edge(node, neighbor)

        if verbose:
            i += 1
            per = i / total
            print("Flagged Backbone : {disjunction:s} : {i:d} of {total:d} nodes processed ({per:.2%})".format(i=i, total=total, per=per, disjunction=disjunction.__name__))

        if B.number_of_edges() == G.number_of_edges():
            break    

    if self_loops:
        G = _remove_semi_triangular_self_loops(G, weight=weight, disjunction=disjunction)
   
    if distortion:
        svals = _compute_distortions(D, G, weight=weight, disjunction=disjunction)
        return G, svals

    return G

    
def _iterative_backbone(D: nx.Graph | nx.DiGraph, weight: str, disjunction: Callable, distortion: bool, self_loops: bool, cutoff: int, verbose: bool) -> nx.Graph | nx.DiGraph | tuple[nx.Graph | nx.DiGraph, dict]:
    """
    Compute the distance backbone using the iterative algorithm.

    For each node in a weighted graph, use Dijkstra's algorithm to find the shortest path to each neighbor. 
    If the direct edge is not the shortest path, remove it.

    Parameters
    ----------
    D : Directed or undirected NetworkX graph
        A weighted distance graph.
    weight : str
        Edge property containing distance values.
    disjunction : Callable
        Function used to measure path distance.
    distortion : bool
        Whether to compute and return the edge distortions of edges not in the backbone.
    self_loops : bool
        Whether to remove self-loops that have a shorter path back to the same node.
    cutoff : int
        Maximum number of connections to be searched per path.
    verbose : bool
        Whether to display computation progress.

    Returns
    -------
    nx.Graph or nx.DiGraph
        The distance backbone.
    tuple of (nx.Graph or nx.DiGraph, dict)
        Edge distortions, returned with the backbone when ``distortion=True``.
    """

    G = D.copy()
    
    if verbose:
        total = G.number_of_nodes()
        i = 0
    
    for node in list(G.nodes()):
        shortest_paths_to_neighbors = single_source_neighbors_dijkstra_path_length(G, source=node, weight=weight, disjunction=disjunction, cutoff=cutoff)

        for neighbor in list(G.neighbors(node)):
            shortest_path = shortest_paths_to_neighbors[neighbor]
            direct_path = G[node][neighbor][weight]

            if shortest_path < direct_path:
                G.remove_edge(node, neighbor)

        if verbose:
            i += 1
            per = i/total
            print("Iterative Backbone : {disjunction:s} : {i:d} of {total:d} nodes processed ({per:.2%})".format(i=i, total=total, per=per, disjunction=disjunction.__name__))

    if self_loops:
        G = _remove_semi_triangular_self_loops(G, weight=weight, disjunction=disjunction)
     
    if distortion:
        svals = _compute_distortions(D, G, weight=weight, disjunction=disjunction, self_loops=self_loops)    
        return G, svals

    return G


def _closure_backbone(D: nx.Graph | nx.DiGraph, weight: str, kind: str, disjunction: Callable, distortion: bool, self_loops: bool, cutoff: int, verbose: bool) -> nx.Graph | nx.DiGraph | tuple[nx.Graph | nx.DiGraph, dict]:
    """
    Compute the distance backbone using the closure algorithm. 

    Compute the distance closure. If a direct edge is not labeled as a shortest path, remove it.

    Parameters
    ----------
    D : Directed or undirected NetworkX graph
        A weighted distance graph.
    kind : {"metric", "ultrametric"}
        Distance metric used to compute the backbone. 
    weight : str
        Edge property containing distance values.
    disjunction : Callable
        Function used to measure path distance.
    distortion : bool
        Whether to compute and return the edge distortions of edges not in the backbone.
    self_loops : bool
        Whether to remove self-loops that have a shorter path back to the same node.
    cutoff : int
        Maximum number of connections to be searched per path.
    verbose : bool
        Whether to display computation progress.

    Returns
    -------
    nx.Graph or nx.DiGraph
        The distance backbone.
    tuple of (nx.Graph or nx.DiGraph, dict)
        Edge distortions, returned with the backbone when ``distortion=True``.
    """

    G = D.copy()
    DC = distance_closure(G, kind=kind, weight=weight, existing_edges_only=True, self_loops=self_loops, verbose=verbose)

    is_kind = 'is_{kind:s}'.format(kind=kind)
    metric_edges = [(u, v) for u, v in DC.edges() if DC[u][v][is_kind]]
    G = DC.edge_subgraph(metric_edges).copy()
    
    if distortion:
        svals = _compute_distortions(D, G, weight=weight, kind=kind, self_loops=self_loops)
        return G, svals

    return G


def _heuristic_backbone(D: nx.Graph | nx.DiGraph, weight: str, disjunction: Callable, distortion: bool, self_loops: bool, cutoff: int, verbose: bool) -> nx.Graph | nx.DiGraph | tuple[nx.Graph | nx.DiGraph, dict]:
    """
    Compute the distance backbone using an algorithm based on "V. Kalavri et al (2016) Proceedings of the VLDB Endowment, Volume 9, Issue 9".

    Parameters
    ----------
    D : Directed or undirected NetworkX graph
        A weighted distance graph.
    weight : str
        Edge property containing distance values.
    disjunction : Callable
        Function used to measure path distance.
    distortion : bool
        Whether to compute and return the edge distortions of edges not in the backbone.
    self_loops : bool
        Whether to remove self-loops that have a shorter path back to the same node.
    cutoff : int
        Maximum number of connections to be searched per path.
    verbose : bool
        Whether to display computation progress.

    Returns
    -------
    nx.Graph or nx.DiGraph
        The distance backbone.
    tuple of (nx.Graph or nx.DiGraph, dict)
        Edge distortions, returned with the backbone when ``distortion=True``.
    """

    G = D.copy()

    total = None
    if verbose: 
        total = G.number_of_nodes()
        i = 0

    # Algorithm 1, page 676
    G = _local_semi_triangles(G, disjunction=disjunction, weight=weight, total=total, verbose=verbose)

    # Algorithm 2, page 677
    backbone_edges = _local_triangular_edges(G, disjunction=disjunction, weight=weight, total=total, verbose=verbose)
    # print("Heuristic Backbone : Algorithm 2 : Complete")

    metric_backbone = {(source, target) for source, target, _ in backbone_edges}
    unlabeled_edges = [(source, target) for source, target in G.edges() if (source, target) not in metric_backbone]

    if verbose:
        total = len(unlabeled_edges)
    
    # Algorithm 3, page 677
    remaining_metric_edges = []
    for source, target in unlabeled_edges:
        path = single_source_target_dijkstra_path(G, source=source, target=target, weight=weight, disjunction=disjunction, cutoff=cutoff)
        
        path_weights = [G[path[idx-1]][path[idx]][weight] for idx in range(1, len(path))]
        shortest_path_length = disjunction(path_weights)

        if G[source][target][weight] <= shortest_path_length:
            remaining_metric_edges.append((source, target))

        if verbose:
            i += 1
            per = i / total
            print("Heuristic Backbone : Algorithm 3 : {disjunction:s} : {i:d} of {total:d} unlabeled edges processed ({per:.2%})".format(i=i, total=total, per=per, disjunction=disjunction.__name__))
    
    final_edges = list(metric_backbone) + remaining_metric_edges
    G = G.edge_subgraph(final_edges).copy()

    if self_loops:
        G = _remove_semi_triangular_self_loops(G, weight=weight, disjunction=disjunction)

    # Compute Distortion
    if distortion:
        svals = _compute_distortions(D, G, weight=weight, disjunction=disjunction, self_loops=self_loops)
        return G, svals
    
    return G


def _approximate_backbone(D: nx.Graph | nx.DiGraph, weight: str, disjunction: Callable, distortion: bool, self_loops: bool, cutoff: int, verbose: bool) -> nx.Graph | nx.DiGraph | tuple[nx.Graph | nx.DiGraph, dict]:
    """
    Compute an approximate distance backbone using an algorithm based on "V. Kalavri et al (2016) Proceedings of the VLDB Endowment, Volume 9, Issue 9".

    Parameters
    ----------
    D : Directed or undirected NetworkX graph
        A weighted distance graph.
    weight : str
        Edge property containing distance values.
    disjunction : Callable
        Function used to measure path distance.
    distortion : bool
        Whether to compute and return the edge distortions of edges not in the backbone.
    self_loops : bool
        Whether to remove self-loops that have a shorter path back to the same node.
    cutoff : int
        Maximum number of connections to be searched per path.
    verbose : bool
        Whether to display computation progress.

    Returns
    -------
    nx.Graph or nx.DiGraph
        The distance backbone.
    tuple of (nx.Graph or nx.DiGraph, dict)
        Edge distortions, returned with the backbone when ``distortion=True``.
    """
    G = D.copy()

    total = None
    if verbose:
        total = G.number_of_nodes()

    # Algorithm 1, page 676
    G = _local_semi_triangles(G, disjunction=disjunction, weight=weight, total=total, verbose=verbose)

    if self_loops:
        G = _remove_semi_triangular_self_loops(G, weight=weight, disjunction=disjunction)

    # Compute Distortion
    if distortion:
        svals = _compute_distortions(D, G, weight=weight, disjunction=disjunction, self_loops=self_loops)
        return G, svals
    
    return G


def _drastic_disjunction(iterable: list[float]) -> float:
    """
    Compute the drastic disjunction of two distances.

    Parameters
    ----------
    iterable : list of float
        Distance values to combine.

    Returns
    -------
    float
        The nonzero distance if one value is zero; otherwise infinity.
    """
    iterable.sort()
    if iterable[0] == 0.0:
        return iterable[1]
    else:
        return np.inf   


def _remove_semi_triangular_self_loops(G: nx.Graph | nx.DiGraph, weight: str, disjunction: Callable) -> nx.Graph | nx.DiGraph:
    """
    Remove self-loops that are semi-triangular, i.e., there exists a neighbor k of u such that the path u -> k -> u is shorter than the self-loop u -> u.

    Parameters
    ----------
    G : Directed or undirected NetworkX graph
        A weighted distance graph.
    weight : str
        Edge property containing distance values.
    disjunction : Callable
        Function used to measure path distance.
    """

    edges_to_remove = []
    for u in nx.nodes_with_selfloops(G):
        length = G[u][u][weight]
        for k in G.neighbors(u):
            if k != u:
                return_path_length = single_source_neighbors_dijkstra_path_length(G, source=k, weight=weight, disjunction=disjunction)
                spl = disjunction([G[u][k][weight], return_path_length[u]])
                if spl < length:
                    edges_to_remove.append((u, u))
                    break

    G.remove_edges_from(edges_to_remove)
    
    return G


def _local_semi_triangles(graph: nx.Graph | nx.DiGraph, disjunction: Callable, weight: str = 'weight', total: int = None, verbose: bool = False) -> nx.Graph | nx.DiGraph:
    """
    Implements Algorithm 1 from "V. Kalavri et al (2016) Proceedings of the VLDB Endowment, Volume 9, Issue 9"
    """

    if verbose:
        i = 0

    for a in graph.nodes():
        neighbors = list(graph[a])
        triangles_to_check = product(neighbors, neighbors)
        for b, c in triangles_to_check:
            if graph.has_edge(a, c) and graph.has_edge(c, b) and graph.has_edge(a, b):
                ac = graph[a][c][weight]
                cb = graph[c][b][weight]
                ab = graph[a][b][weight]
                if disjunction([ cb, ac ]) < ab:
                    graph.remove_edge(a, b)

        if verbose:
            i += 1
            per = i / total
            print("Heuristic Backbone : Algorithm 1 : {disjunction:s} : {i:d} of {total:d} nodes processed ({per:.2%})".format(i=i, total=total, per=per, disjunction=disjunction.__name__))

    return graph


def _local_triangular_edges(graph: nx.Graph | nx.DiGraph, disjunction: Callable, weight: str = 'weight', total: int = None, verbose: bool = False) -> nx.Graph | nx.DiGraph:
    """
    Implements Algorithm 2 from "V. Kalavri et al (2016) Proceedings of the VLDB Endowment, Volume 9, Issue 9"
    """

    if verbose:
        i = 0

    U = {}
    for source in graph.nodes():
        neighbors = [(source, target, data[weight]) for target, data in graph[source].items()]
        U[source] = sorted(neighbors, key=lambda item: item[2])

    metric_edges = set()
    for source in graph.nodes():
        if verbose:
            i += 1
            per = i / total
            print("Heuristic Backbone : Algorithm 2 : {disjunction:s} : {i:d} of {total:d} nodes processed before termination ({per:.2%})".format(i=i, total=total, per=per, disjunction=disjunction.__name__))

        if not U[source]:
            continue

        weights_for_comparison = set()
        metric = True

        removed_pair = U[source].pop(0)
        metric_edges.add(removed_pair)
        
        while U[source]:
            e = U[source].pop(0)
            for _, target, _ in metric_edges:
                if graph.has_edge(source, target) and U[target]:
                    w_x = disjunction([graph[source][target][weight], U[target][0][2]])
                    weights_for_comparison.add(w_x)
            
            for w in weights_for_comparison:
                if e[2] > w:
                    metric = False
                    break

            if metric:
                metric_edges.add(e)
                weights_for_comparison = set()
            else:
                return metric_edges

    return metric_edges


def _compute_distortions(D: nx.Graph | nx.DiGraph, B: nx.Graph | nx.DiGraph, disjunction: Callable, weight: str, self_loops: bool) -> dict:
    """
    Compute distortions of edges not in the backbone.

    Parameters
    ----------
    D : Directed or undirected NetworkX distance graph
        The weighted distance graph
    B : Directed or undirected NetworkX backbone graph
        The weighted backbone subgraph
    weight : str
        Edge property containing distance values.
    disjunction : Callable
        Function used to measure path distance.
    self_loops : bool
        Whether to remove self-loops that have a shorter path back to the same node.

    Returns
    -------
    dict
        Dictionary keyed by edge with its distortion value.
    
    """
    G = D.copy()
    G.remove_edges_from(B.edges())

    sloops = dict()
    if self_loops:
        for u in nx.nodes_with_selfloops(G):
            length = G[u][u][weight]
            for k in G.neighbors(u):
                return_path_length = single_source_neighbors_dijkstra_path_length(B, source=k, weight=weight, disjunction=disjunction)
                spl = disjunction([G[u][k][weight], return_path_length[u]])
                if spl < length:
                    length = spl
            sloops[u] = length

    svals = dict()        
    for u in G.nodes():
        metric_dist = single_source_neighbors_dijkstra_path_length(B, source=u, weight=weight, disjunction=disjunction)
        for v in G.neighbors(u):
            if (v == u) and self_loops:
                svals[(u, v)] = G[u][v][weight]/sloops[u]
            else:
                svals[(u, v)] = G[u][v][weight]/metric_dist[v]
    
    return svals   

_BACKBONE_ALGORITHMS = {
    "iterative": _iterative_backbone,
    "flagged": _flagged_backbone,
    "closure": _closure_backbone,
    "heuristic": _heuristic_backbone,
    "approximate": _approximate_backbone
}

_KINDS = {
    "metric": sum,
    "ultrametric": max,
    "drastic": _drastic_disjunction
}
