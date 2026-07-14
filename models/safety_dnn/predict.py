"""
SafetyNet Inference
====================
Load trained weights and predict S_infra for H3 hex cells.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch

from models.safety_dnn.network import SafetyNet

DEFAULT_WEIGHTS_PATH = Path(__file__).parent / "weights" / "safety_net.pth"


class SafetyPredictor:
    """
    Wraps a trained SafetyNet model for CPU inference.

    Parameters
    ----------
    input_dim : int
        Must match the dimension the model was trained on.
    weights_path : Path | str
        Path to the saved `.pth` state dict.
    """

    def __init__(
        self,
        input_dim: int = 10,
        weights_path: Path | str = DEFAULT_WEIGHTS_PATH,
    ):
        self.model = SafetyNet(input_dim=input_dim)
        weights_path = Path(weights_path)

        if weights_path.exists():
            self.model.load_state_dict(
                torch.load(weights_path, map_location="cpu", weights_only=True)
            )
            self.model.eval()
            self._loaded = True
        else:
            self._loaded = False
            print(
                f"[SafetyPredictor] WARNING: Weights not found at {weights_path}. "
                "Predictions will be random (untrained model)."
            )

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @torch.no_grad()
    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        Predict S_infra scores for a batch of H3 cell feature vectors.

        Parameters
        ----------
        features : np.ndarray
            Shape (n_cells, input_dim).

        Returns
        -------
        np.ndarray
            Shape (n_cells,) — safety scores in [0, 1].
        """
        X = torch.tensor(features, dtype=torch.float32)
        scores = self.model(X).squeeze(-1).numpy()
        return scores

    def predict_single(self, features: np.ndarray) -> float:
        """Predict S_infra for a single cell. Returns a Python float."""
        return float(self.predict(features.reshape(1, -1))[0])
