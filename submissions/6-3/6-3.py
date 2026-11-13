"""課題6-3：交差検証のJump予測確率からROC曲線とAUCを求める。"""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", nargs="?", type=Path,
                        default=Path("lessons/06-evaluation/output/6-1/predictions.csv"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("lessons/06-evaluation/output/6-3"))
    args = parser.parse_args()
    with args.predictions.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    if {r["true_label"] for r in rows} != {"walk", "jump", "squat"}:
        raise ValueError("walk / jump / squatの評価結果を指定してください。")
    truth = np.array([r["true_label"] == "jump" for r in rows])
    scores = np.array([float(r["prob_jump"]) for r in rows])
    if not np.isfinite(scores).all() or np.any((scores < 0) | (scores > 1)):
        raise ValueError("予測確率が0〜1の範囲にありません。")
    fpr, tpr, thresholds = roc_curve(truth, scores, drop_intermediate=False)
    auc = roc_auc_score(truth, scores)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    with (out / "auc.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("positive_label", "positive_windows", "negative_windows", "auc"))
        writer.writerow(("jump", int(truth.sum()), int((~truth).sum()), auc))
    with (out / "roc_points.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("threshold", "fpr", "tpr"))
        writer.writerows(zip(thresholds, fpr, tpr))
    fig, ax = plt.subplots(figsize=(6.2, 5.2), layout="constrained")
    ax.plot(fpr, tpr, color="#0072B2", linewidth=2, label=f"AUC = {auc:.4f}")
    ax.plot([0, 1], [0, 1], color="#666666", linestyle="--", label="Chance ranking")
    ax.set(title="ROC: Jump vs. Walk / Squat", xlabel="False positive rate (1 - specificity)",
           ylabel="True positive rate (recall)", xlim=(0, 1), ylim=(0, 1.02))
    ax.grid(alpha=0.25)
    ax.legend(loc="lower right")
    fig.savefig(out / "roc.png", dpi=180)
    plt.close(fig)
    print(f"Jump vs. others AUC={auc:.6f}")


if __name__ == "__main__":
    main()
