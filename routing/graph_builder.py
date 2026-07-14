"""
Road Graph Builder
===================
DESIGN.md §3, §5.1: Download the Patna road network via OSMnx and
construct a NetworkX graph suitable for routing.

The graph is built once at startup and cached in memory.
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import osmnx as ox

# ── Patna bounding box (approximate urban area) ────────
PATNA_PLACE_NAME = "Patna, Bihar, India"

# Cache path for the GraphML file (avoids re-downloading)
GRAPH_CACHE_PATH = Path("data") / "patna_road_graph.graphml"


def download_patna_graph(
    network_type: str = "drive",
    simplify: bool = True,
) -> nx.MultiDiGraph:
    """
    Download the Patna road network from OpenStreetMap via OSMnx.

    Parameters
    ----------
    network_type : str
        Type of street network ('drive', 'walk', 'bike', 'all').
    simplify : bool
        If True, simplify the graph topology.

    Returns
    -------
    nx.MultiDiGraph
        OSMnx road network graph with node/edge attributes.
    """
    print(f"[GraphBuilder] Downloading '{network_type}' network for {PATNA_PLACE_NAME}...")
    G = ox.graph_from_place(PATNA_PLACE_NAME, network_type=network_type, simplify=simplify)
    print(f"[GraphBuilder] Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G


def save_graph(G: nx.MultiDiGraph, path: Path = GRAPH_CACHE_PATH) -> None:
    """Save graph to GraphML for fast reloading."""
    path.parent.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(G, filepath=str(path))
    print(f"[GraphBuilder] Graph saved → {path}")


def load_graph(path: Path = GRAPH_CACHE_PATH) -> nx.MultiDiGraph:
    """Load a previously saved graph from disk."""
    if not path.exists():
        raise FileNotFoundError(
            f"Graph cache not found at {path}. "
            "Run `download_patna_graph()` first or execute notebook 01."
        )
    G = ox.load_graphml(str(path))
    print(f"[GraphBuilder] Graph loaded from cache: {G.number_of_nodes()} nodes")
    return G


def get_or_download_graph(
    network_type: str = "drive",
    force_download: bool = False,
) -> nx.MultiDiGraph:
    """
    Load from cache if available, otherwise download and cache.

    Parameters
    ----------
    force_download : bool
        If True, re-download even if cache exists.
    """
    if GRAPH_CACHE_PATH.exists() and not force_download:
        return load_graph()

    G = download_patna_graph(network_type=network_type)
    save_graph(G)
    return G
