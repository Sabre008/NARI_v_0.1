"""
SafetyNet Training Loop
========================
DESIGN.md §2A: Pre-trained on synthetic data, fine-tuned with verified reports.

Usage (from project root):
    python -m models.safety_dnn.train --epochs 100 --lr 0.001
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split

from models.safety_dnn.network import SafetyNet

# ── Default paths ───────────────────────────────────────
WEIGHTS_DIR = Path(__file__).parent / "weights"
DEFAULT_WEIGHTS_PATH = WEIGHTS_DIR / "safety_net.pth"
DEFAULT_DATA_PATH = Path("data") / "patna_synthetic_training_data.csv"

# ── The 10 feature columns produced by notebooks 01 & 02 ─
FEATURE_COLS = [
    "count_hospital",
    "count_police",
    "count_residential",
    "count_commercial",
    "count_hotel",
    "count_fire_station",
    "count_school",
    "count_bank",
    "count_bus_stop",
    "count_intersections",
]
TARGET_COL = "target_safety_score"
INPUT_DIM = len(FEATURE_COLS)  # 10


def load_training_data(
    data_path: Path = DEFAULT_DATA_PATH,
    test_size: float = 0.2,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load the synthetic training CSV and split into train/validation sets.

    Returns
    -------
    tuple
        (X_train, X_val, y_train, y_val) as numpy float32 arrays.
    """
    if not data_path.exists():
        raise FileNotFoundError(
            f"Training data not found at {data_path}. "
            "Run notebooks/02_synthetic_data_gen.ipynb first."
        )

    df = pd.read_csv(data_path)
    print(f"[SafetyNet] Loaded {len(df):,} samples from {data_path}")

    X = df[FEATURE_COLS].values.astype(np.float32)
    y = df[TARGET_COL].values.astype(np.float32)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=test_size, random_state=42,
    )
    print(f"[SafetyNet] Train: {len(X_train):,}  |  Val: {len(X_val):,}")

    return X_train, X_val, y_train, y_val


def build_dataloader(
    features: np.ndarray,
    labels: np.ndarray,
    batch_size: int = 32,
    shuffle: bool = True,
) -> DataLoader:
    """Wrap numpy arrays into a PyTorch DataLoader."""
    X = torch.tensor(features, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.float32).unsqueeze(1)
    return DataLoader(TensorDataset(X, y), batch_size=batch_size, shuffle=shuffle)


def train_model(
    model: SafetyNet,
    train_loader: DataLoader,
    val_loader: DataLoader | None = None,
    epochs: int = 100,
    lr: float = 1e-3,
    save_path: Path = DEFAULT_WEIGHTS_PATH,
) -> dict[str, list[float]]:
    """
    Train the SafetyNet model on CPU, validate each epoch, and save weights.

    Returns
    -------
    dict
        {"train_loss": [...], "val_loss": [...]} per-epoch histories.
    """
    device = torch.device("cpu")
    model = model.to(device)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    history: dict[str, list[float]] = {"train_loss": [], "val_loss": []}
    best_val_loss = float("inf")

    for epoch in range(1, epochs + 1):
        # ── Training ────────────────────────────────────
        model.train()
        epoch_loss = 0.0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            preds = model(X_batch)
            loss = criterion(preds, y_batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * X_batch.size(0)

        avg_train = epoch_loss / len(train_loader.dataset)  # type: ignore[arg-type]
        history["train_loss"].append(avg_train)

        # ── Validation ──────────────────────────────────
        avg_val = 0.0
        if val_loader is not None:
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for X_batch, y_batch in val_loader:
                    X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                    preds = model(X_batch)
                    val_loss += criterion(preds, y_batch).item() * X_batch.size(0)
            avg_val = val_loss / len(val_loader.dataset)  # type: ignore[arg-type]
            history["val_loss"].append(avg_val)

            # Save best model
            if avg_val < best_val_loss:
                best_val_loss = avg_val
                save_path.parent.mkdir(parents=True, exist_ok=True)
                torch.save(model.state_dict(), save_path)

        # ── Logging ─────────────────────────────────────
        if epoch % 10 == 0 or epoch == 1:
            msg = f"  Epoch {epoch:>3d}/{epochs}  —  Train MSE: {avg_train:.6f}"
            if val_loader is not None:
                msg += f"  |  Val MSE: {avg_val:.6f}"
            print(msg)

    # Final save (in case no val_loader was provided)
    if val_loader is None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), save_path)

    print(f"[SafetyNet] Best weights saved → {save_path}")
    return history


def main():
    """CLI entry point for standalone training."""
    parser = argparse.ArgumentParser(description="Train SafetyNet DNN")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument(
        "--data",
        type=str,
        default=str(DEFAULT_DATA_PATH),
        help="Path to the synthetic training CSV",
    )
    args = parser.parse_args()

    # ── Load data ───────────────────────────────────────
    X_train, X_val, y_train, y_val = load_training_data(Path(args.data))

    train_loader = build_dataloader(X_train, y_train, batch_size=args.batch_size)
    val_loader = build_dataloader(X_val, y_val, batch_size=args.batch_size, shuffle=False)

    # ── Build model ─────────────────────────────────────
    model = SafetyNet(input_dim=INPUT_DIM)
    print(f"[SafetyNet] Architecture: input_dim={INPUT_DIM}, hidden=[64, 32], output=1 (sigmoid)")
    print(f"[SafetyNet] Device: CPU")
    print(f"[SafetyNet] Training for {args.epochs} epochs, lr={args.lr}, batch_size={args.batch_size}")

    # ── Train ───────────────────────────────────────────
    history = train_model(
        model, train_loader, val_loader,
        epochs=args.epochs, lr=args.lr,
    )

    print(f"\n[SafetyNet] Training complete.")
    print(f"  Final train MSE: {history['train_loss'][-1]:.6f}")
    print(f"  Final val MSE:   {history['val_loss'][-1]:.6f}")


if __name__ == "__main__":
    main()
