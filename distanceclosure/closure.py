# -*- coding: utf-8 -*-
"""
Distance Closure
================

Compute the distance closure of a weighted graph.
"""

import numpy as np
import networkx as nx
from typing import Callable
from distanceclosure.dijkstra import all_pairs_dijkstra_path_length, single_source_target_dijkstra_path


__all__ = [
    "distance_closure"
]


_KINDS = {
    "metric": sum,
    "ultrametric": max,
}

def distance_closure(D: nx.Graph | nx.DiGraph, kind: str = 'metric', weight: str = 'weight', existing_edges_only: bool = False, self_loops: bool = False, cutoff: int = None, verbose: bool = False) -> nx.Graph | nx.DiGraph: 
    """
    Compute the distance closure of a weighted graph.

    Parameters
    ----------
    D : Directed or undirected NetworkX graph
        A weighted distance graph.
    kind : {"metric", "ultrametric"}, optional
        Distance metric used to compute the closure. "metric" compares sums while "ultrametric" compares maximums, ``kind="metric"`` by default.
    weight : str, optional
        Edge property containing distance values, ``weight="weight"`` by default.
    existing_edges_only : bool, optional
        Whether to compute closure distances only for existing edges, ``existing_edges_only=False`` by default.
    self_loops : bool, optional
        Whether to compute the closure considering self-loops, ``self_loops=False`` by default.
    cutoff : int, optional
        Maximum number of connections to be searched per path, ``cutoff=None`` by default.
    verbose : bool, optional
        Whether to display computation progress, ``verbose=False`` by default.

    Returns
    -------
    nx.Graph or nx.DiGraph
        A copy of the input graph with closure distance and backbone membership edge attributes.

    Raises
    ------
    ValueError
        If ``kind`` is invalid.
    """

    try:
        disjunction = _KINDS[kind]
    except KeyError:
        raise ValueError("Invalid input. Valid arguments are: {valid_kinds}".format(valid_kinds=_KINDS.keys()))

    return _closure(D, kind=kind, disjunction=disjunction, weight=weight, existing_edges_only=existing_edges_only, self_loops=self_loops, cutoff=cutoff, verbose=verbose)


def _closure(D: nx.Graph | nx.DiGraph, kind: str, disjunction: Callable, weight: str, existing_edges_only: bool, self_loops: bool, cutoff: int, verbose: bool) -> nx.Graph | nx.DiGraph:
    """
    Compute the distance closure using all-pairs shortest paths.

    Parameters
    ----------
    D : Directed or undirected NetworkX graph
        A weighted distance graph.
    kind : {"metric", "ultrametric"}
        Distance metric used to compute the closure. "metric" compares sums while "ultrametric" compares maximums.
    disjunction : Callable
        Function used to measure path distance.
    weight : str
        Edge property containing distance values.
    existing_edges_only : bool
        Whether to compute closure distances only for existing edges.
    self_loops : bool
        Whether to remove self-loops that have a shorter path back to the same node.
    verbose : bool
        Whether to display computation progress.

    Returns
    -------
    nx.Graph or nx.DiGraph
        A copy of the input graph with closure distance and backbone membership edge attributes. Added closure edges contain only the closure distance attribute.
    """

    G = D.copy() 
    edges_seen = set()

    if verbose:
        total = G.number_of_nodes()
        i = 0

    for u, lengths in all_pairs_dijkstra_path_length(G, weight=weight, disjunction=disjunction, cutoff=cutoff):
        for v, length in lengths.items():
            if (u, v) in edges_seen or u == v:
                continue
            else:
                edges_seen.add((u, v))
                kind_distance = '{kind:s}_distance'.format(kind=kind)
                is_kind = 'is_{kind:s}'.format(kind=kind)
                if not G.has_edge(u, v):
                    if not existing_edges_only:
                        G.add_edge(u, v, **{weight: np.inf, kind_distance: length})
                else:
                    G[u][v][kind_distance] = length
                    G[u][v][is_kind] = True if (length == G[u][v][weight]) else False

        if verbose:
            i += 1
            per = i / total
            print("Distance Closure : {kind:s} : {i:d} of {total:d} nodes processed ({per:.2%})".format(kind=kind, i=i, total=total, per=per))

    if self_loops:
        for u in G.nodes():
            if not G.has_edge(u, u):
                length = np.inf
            else:
                length = G[u][u][weight]

            for k in G.neighbors(u):
                return_path = single_source_target_dijkstra_path(G, source=k, target=u, weight=weight, disjunction=disjunction, cutoff=cutoff)
                spl = disjunction([G[u][k][weight], disjunction(G[return_path[idx-1]][return_path[idx]][weight] for idx in range(1, len(return_path)))])
                if spl < length:
                    length = spl

            if not G.has_edge(u, u):
                if not existing_edges_only:
                    G.add_edge(u, u, **{weight: np.inf, kind_distance: length})
            else:
                G[u][u][kind_distance] = length
                G[u][u][is_kind] = True if (length == G[u][u][weight]) else False

    return G


