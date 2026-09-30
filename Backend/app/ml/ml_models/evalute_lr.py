"""
Evaluation metrics for LR fold results: accuracy, precision/recall/F1,
confusion matrix, ROC-AUC, majority-class baseline comparison, calibration check.
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.calibration import calibration_curve

DEFAULT_THRESHOLD = 0.5


def evaluate_fold(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    threshold: float = DEFAULT_THRESHOLD,
    train_majority_label: int = None,
) -> dict:
    """
    Evaluates model performance on a single fold split.
    """
    y_pred = (y_pred_proba >= threshold).astype(int)

    # Majority-class baseline: fallback to test mean only if train_majority_label isn't provided
    if train_majority_label is None:
        train_majority_label = int(np.round(y_true.mean()))

    baseline_preds = np.full_like(y_true, train_majority_label)
    baseline_accuracy = accuracy_score(y_true, baseline_preds)
    acc = accuracy_score(y_true, y_pred)

    metrics = {
        "accuracy": acc,
        "baseline_accuracy": baseline_accuracy,
        "beats_baseline": acc > baseline_accuracy,
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "roc_auc": (
            roc_auc_score(y_true, y_pred_proba)
            if len(set(y_true)) > 1
            else None
        ),
    }

    # Calibration curve with uniform fallback if quantile binning fails
    try:
        prob_true, prob_pred = calibration_curve(
            y_true, y_pred_proba, n_bins=5, strategy="quantile"
        )
        metrics["calibration"] = {
            "predicted_probs": prob_pred.tolist(),
            "actual_frequencies": prob_true.tolist(),
        }
    except ValueError:
        try:
            prob_true, prob_pred = calibration_curve(
                y_true, y_pred_proba, n_bins=5, strategy="uniform"
            )
            metrics["calibration"] = {
                "predicted_probs": prob_pred.tolist(),
                "actual_frequencies": prob_true.tolist(),
            }
        except ValueError:
            metrics["calibration"] = None  # Insufficient variance to bin

    return metrics


def evaluate_all_folds(fold_results: list[dict]) -> list[dict]:
    """
    Evaluates model metrics across all walk-forward validation folds.
    """
    all_metrics = []
    for result in fold_results:
        metrics = evaluate_fold(
            y_true=result["y_true"],
            y_pred_proba=result["y_pred_proba"],
            train_majority_label=result.get("train_majority_label"),
        )
        metrics["fold"] = result["fold"]
        all_metrics.append(metrics)

    return all_metrics


def aggregate_fold_metrics(all_metrics: list[dict]) -> dict:
    """
    Computes mean metrics across all cross-validation folds.
    """
    valid_aucs = [m["roc_auc"] for m in all_metrics if m["roc_auc"] is not None]

    return {
        "mean_accuracy": float(np.mean([m["accuracy"] for m in all_metrics])),
        "mean_baseline_accuracy": float(np.mean([m["baseline_accuracy"] for m in all_metrics])),
        "mean_precision": float(np.mean([m["precision"] for m in all_metrics])),
        "mean_recall": float(np.mean([m["recall"] for m in all_metrics])),
        "mean_f1": float(np.mean([m["f1"] for m in all_metrics])),
        "mean_roc_auc": float(np.mean(valid_aucs)) if valid_aucs else None,
        "folds_beating_baseline": sum(1 for m in all_metrics if m["beats_baseline"]),
        "total_folds": len(all_metrics),
    }