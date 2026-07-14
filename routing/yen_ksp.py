"""
Yen's K-Shortest Paths
========================
DESIGN.md §3: Find K alternative routes for safety-optimised selection.

Uses NetworkX's built-in shortest_simple_paths (Yen's algorithm)
with configurable weight attributes.
"""

from __future__ import annotations

import networkx as nx


def k_shortest_paths(
    G: nx.MultiDiGraph | nx.DiGraph,
    source: int,
    target: int,
    k: int = 5,
    weight: str = "safety_cost",
) -> list[list[int]]:
    """
    Find up to K shortest simple paths using Yen's algorithm.

    Parameters
    ----------
    G : nx.MultiDiGraph | nx.DiGraph
        Road network graph with edge weights.
    source : int
        Origin node ID.
    target : int
        Destination node ID.
    k : int
        Maximum number of paths to return.
    weight : str
        Edge attribute to use as cost.

    Returns
    -------
    list[list[int]]
        Up to K paths, each a list of node IDs.
    """
    # NetworkX needs a DiGraph for shortest_simple_paths
    if isinstance(G, nx.MultiDiGraph):
        DG = nx.DiGraph(G)
    else:
        DG = G

    paths: list[list[int]] = []
    try:
        for i, path in enumerate(
            nx.shortest_simple_paths(DG, source, target, weight=weight)
        ):
            paths.append(path)
            if i + 1 >= k:
                break
    except nx.NetworkXNoPath:
        pass

    return paths


def path_total_weight(
    G: nx.MultiDiGraph | nx.DiGraph,
    path: list[int],
    weight: str = "length",
) -> float:
    """
    Sum edge weights along a path.

    Parameters
    ----------
    path : list[int]
        Ordered list of node IDs.
    weight : str
        Edge attribute to sum.

    Returns
    -------
    float
        Total weight of the path.
    """
    total = 0.0
    for u, v in zip(path[:-1], path[1:]):
        edge_data = G.get_edge_data(u, v)
        if edge_data is None:
            continue
        # Handle MultiDiGraph (take first edge)
        if isinstance(edge_data, dict) and 0 in edge_data:
            edge_data = edge_data[0]
        total += edge_data.get(weight, 0.0)
    return total
