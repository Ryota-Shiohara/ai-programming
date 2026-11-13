"""課題6-2：5分割の評価予測を結合した混同行列とクラス別指標。"""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support


LABELS = ("walk", "jump", "squat")


def write_csv(path, header, rows):
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", nargs="?", type=Path,
                        default=Path("lessons/06-evaluation/output/6-1/predictions.csv"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("lessons/06-evaluation/output/6-2"))
    args = parser.parse_args()
    with args.predictions.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    truth = [r["true_label"] for r in rows]
    pred = [r["predicted_label"] for r in rows]
    if set(truth) != set(LABELS) or not set(pred) <= set(LABELS):
        raise ValueError("walk / jump / squatの評価結果を指定してください。")
    counts = confusion_matrix(truth, pred, labels=LABELS)
    rates = counts / counts.sum(axis=1, keepdims=True)
    precision, recall, f1, support = precision_recall_fscore_support(
        truth, pred, labels=LABELS, zero_division=0)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    for name, matrix in (("counts", counts), ("true_class_rates", rates)):
        write_csv(out / f"confusion_{name}.csv", ("true_label", *LABELS),
                  [(label, *row) for label, row in zip(LABELS, matrix)])
    write_csv(out / "class_metrics.csv", ("label", "precision", "recall", "f1", "support"),
              zip(LABELS, precision, recall, f1, support))
    accuracy, macro_f1 = accuracy_score(truth, pred), float(f1.mean())
    write_csv(out / "overall_metrics.csv", ("windows", "accuracy", "macro_f1"),
              [(len(truth), accuracy, macro_f1)])

    fig, axes = plt.subplots(1, 2, figsize=(9, 4.4), layout="constrained")
    for ax, title, matrix, fmt in zip(axes, ("Window counts", "Within each true class"),
                                      (counts, rates), ("d", ".1%")):
        ax.imshow(matrix, cmap="Blues", vmin=0)
        for i, j in np.ndindex(matrix.shape):
            ax.text(j, i, format(matrix[i, j], fmt), ha="center", va="center",
                    color="white" if matrix[i, j] > matrix.max() * 0.55 else "black")
        ax.set(title=title, xlabel="Predicted label", ylabel="True label")
        ax.set_xticks(range(3), labels=LABELS)
        ax.set_yticks(range(3), labels=LABELS)
    fig.savefig(out / "confusion.png", dpi=180)
    plt.close(fig)
    print(f"Accuracy={accuracy:.4%}, Macro F1={macro_f1:.6f}")


if __name__ == "__main__":
    main()
