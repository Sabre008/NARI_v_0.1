"""Tests for models.trust_engine — Isolation Forest and time-decay."""

import math
from datetime import datetime, timezone, timedelta

import numpy as np

from models.trust_engine.isolation_forest import ReportVerifier
from models.trust_engine.decay import compute_decayed_weight, aggregate_crowd_score


class TestReportVerifier:
    def test_unfitted_accepts_all(self):
        """An untrained verifier should accept all reports (safe default)."""
        verifier = ReportVerifier(model_path="nonexistent.joblib")
        features = np.array([1.0, 30.0, 2.0, 0.5, 1.0])
        assert verifier.verify(features) is True

    def test_fit_and_verify(self):
        """After fitting, the model should be able to classify inliers."""
        verifier = ReportVerifier(model_path="test_model.joblib")
        # Generate normal data
        rng = np.random.default_rng(42)
        normal_data = rng.normal(loc=5.0, scale=1.0, size=(100, 5))
        verifier.fit(normal_data)
        assert verifier.is_fitted

        # A normal point should be verified
        normal_point = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
        assert verifier.verify(normal_point) is True


class TestDecay:
    def test_decay_at_zero_time(self):
        """Decay at t=0 should return the raw rating."""
        now = datetime.now(timezone.utc)
        w = compute_decayed_weight(5, now, current_time=now, decay_lambda=0.05)
        assert abs(w - 5.0) < 1e-6

    def test_decay_reduces_over_time(self):
        """Weight should decrease as time passes."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=24)
        w = compute_decayed_weight(5, past, current_time=now, decay_lambda=0.05)
        expected = 5 * math.exp(-0.05 * 24)
        assert abs(w - expected) < 1e-6
        assert w < 5.0

    def test_aggregate_empty(self):
        """No ratings should return neutral 0.5."""
        assert aggregate_crowd_score([]) == 0.5
