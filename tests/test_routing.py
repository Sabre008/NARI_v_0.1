"""Tests for routing — Yen's KSP and distance constraint."""

from routing.yen_ksp import k_shortest_paths, path_total_weight
from routing.constraints import filter_by_distance_constraint


def test_k_shortest_paths(sample_graph):
    """Should find at least one path from A to E."""
    paths = k_shortest_paths(sample_graph, "A", "E", k=3, weight="length")
    assert len(paths) >= 1
    assert paths[0][0] == "A"
    assert paths[0][-1] == "E"


def test_path_total_weight(sample_graph):
    """Weight computation should sum edge attributes along path."""
    path = ["A", "B", "D", "E"]
    total = path_total_weight(sample_graph, path, weight="length")
    assert abs(total - 6.0) < 1e-6  # 2 + 3 + 1


def test_distance_constraint(sample_graph):
    """Paths exceeding 1.25× shortest should be filtered out."""
    paths = k_shortest_paths(sample_graph, "A", "E", k=5, weight="length")
    shortest_dist = path_total_weight(sample_graph, paths[0], weight="length")

    filtered = filter_by_distance_constraint(
        sample_graph, paths,
        shortest_distance=shortest_dist,
        max_detour_factor=1.25,
        weight="length",
    )

    for path, dist in filtered:
        assert dist <= 1.25 * shortest_dist
