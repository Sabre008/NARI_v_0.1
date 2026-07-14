"""
Shared test fixtures for N.A.R.I test suite.
"""

import pytest
import networkx as nx


@pytest.fixture
def sample_graph() -> nx.DiGraph:
    """
    A small weighted graph for routing tests.

    Layout:
        A --2-- B --3-- D
        |               |
        4              1
        |               |
        C ------5------ E
    """
    G = nx.DiGraph()
    G.add_edge("A", "B", length=2.0, safety_cost=0.3)
    G.add_edge("B", "D", length=3.0, safety_cost=0.2)
    G.add_edge("A", "C", length=4.0, safety_cost=0.1)
    G.add_edge("C", "E", length=5.0, safety_cost=0.4)
    G.add_edge("D", "E", length=1.0, safety_cost=0.1)
    G.add_edge("B", "C", length=1.5, safety_cost=0.5)
    return G
