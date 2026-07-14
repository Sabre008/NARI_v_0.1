"""
SafetyNet — PyTorch MLP for Infrastructure Safety Scoring
===========================================================
DESIGN.md §2A: DNN Regression Model applied to H3 hexagonal grid cells.

Architecture:
    Input  →  infrastructure feature vector (hospitals, streetlights,
              police stations, intersection count, OSM land-use tags)
    Output →  S_infra ∈ [0.0, 1.0]  (sigmoid-activated scalar)

The network is intentionally lightweight (3-layer MLP) for CPU inference.
"""

import torch
import torch.nn as nn


class SafetyNet(nn.Module):
    """
    Multi-Layer Perceptron for predicting base infrastructure safety.

    Parameters
    ----------
    input_dim : int
        Number of infrastructure features per H3 cell.
    hidden_dims : list[int]
        Sizes of hidden layers. Default: [64, 32].
    dropout : float
        Dropout probability between layers. Default: 0.2.
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dims: list[int] | None = None,
        dropout: float = 0.2,
    ):
        super().__init__()
        if hidden_dims is None:
            hidden_dims = [64, 32]

        layers: list[nn.Module] = []
        prev_dim = input_dim

        for h_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, h_dim),
                nn.BatchNorm1d(h_dim),
                nn.ReLU(),
                nn.Dropout(dropout),
            ])
            prev_dim = h_dim

        # Output layer: single sigmoid-activated score
        layers.append(nn.Linear(prev_dim, 1))
        layers.append(nn.Sigmoid())

        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Parameters
        ----------
        x : torch.Tensor
            Batch of feature vectors, shape (batch_size, input_dim).

        Returns
        -------
        torch.Tensor
            Predicted S_infra scores, shape (batch_size, 1).
        """
        return self.network(x)
