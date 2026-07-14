"""
Isolation Forest Anomaly Detection for Crowd Reports
======================================================
DESIGN.md §2C: Unsupervised model to identify spam/malicious reports
based on account history and submission velocity.

Features used for anomaly detection:
    - User trust score
    - Time since account creation (days)
    - Number of reports submitted in last 24 hours
    - Standard deviation of user's past ratings
    - Distance from user's typical reporting area
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from sklearn.ensemble import IsolationForest
import joblib


DEFAULT_MODEL_PATH = Path(__file__).parent / "anomaly_detector.joblib"


class ReportVerifier:
    """
    Wraps an Isolation Forest to verify the authenticity of crowd reports.

    A report is flagged as anomalous (unverified) if the model predicts -1.
    """

    def __init__(
        self,
        contamination: float = 0.1,
        model_path: Path | str = DEFAULT_MODEL_PATH,
    ):
        self.model_path = Path(model_path)
        self.contamination = contamination

        if self.model_path.exists():
            self.model: IsolationForest = joblib.load(self.model_path)
            self._fitted = True
        else:
            self.model = IsolationForest(
                contamination=contamination,
                n_estimators=100,
                random_state=42,
            )
            self._fitted = False

    @property
    def is_fitted(self) -> bool:
        return self._fitted

    def fit(self, feature_matrix: np.ndarray) -> None:
        """
        Fit the Isolation Forest on historical report features.

        Parameters
        ----------
        feature_matrix : np.ndarray
            Shape (n_reports, n_features). See module docstring for features.
        """
        self.model.fit(feature_matrix)
        self._fitted = True

        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"[ReportVerifier] Model saved → {self.model_path}")

    def verify(self, features: np.ndarray) -> bool:
        """
        Check whether a single report is genuine.

        Parameters
        ----------
        features : np.ndarray
            Shape (1, n_features) or (n_features,).

        Returns
        -------
        bool
            True if the report is considered genuine (inlier), False if anomalous.
        """
        if not self._fitted:
            # Default to accepting reports when the model is untrained
            return True

        X = features.reshape(1, -1) if features.ndim == 1 else features
        prediction = self.model.predict(X)[0]
        return prediction == 1  # 1 = inlier, -1 = outlier
