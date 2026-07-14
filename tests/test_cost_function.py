"""Tests for routing.cost_function — S_total computation."""

from routing.cost_function import compute_edge_safety, safety_to_cost


def test_compute_edge_safety_basic():
    """S_total with neutral inputs should return a reasonable value."""
    score = compute_edge_safety(
        s_infra=0.8, m_demo=1.0, crowd_decay=0.5, news_severity=0.0,
        alpha=0.3, beta=0.2,
    )
    # (0.8 * 1.0) + (0.3 * 0.5) - (0.2 * 0.0) = 0.8 + 0.15 = 0.95
    assert abs(score - 0.95) < 1e-6


def test_compute_edge_safety_clamped():
    """S_total should never exceed 1.0 or go below 0.0."""
    high = compute_edge_safety(1.0, 1.0, 1.0, 0.0, alpha=0.5, beta=0.1)
    assert high <= 1.0

    low = compute_edge_safety(0.0, 0.67, 0.0, 1.0, alpha=0.3, beta=1.5)
    assert low >= 0.0


def test_safety_to_cost_inversion():
    """Cost should be the inverse of safety."""
    assert safety_to_cost(1.0) == 0.0
    assert safety_to_cost(0.0) == 1.0
    assert abs(safety_to_cost(0.7) - 0.3) < 1e-6
