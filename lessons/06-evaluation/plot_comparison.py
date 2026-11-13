"""6-1のFold別指標と6-4のSubject別指標を並べた考察用の図を作る。"""

import csv
from pathlib import Path
from statistics import mean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from sklearn.metrics import f1_score


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def main():
    output = Path(__file__).resolve().parent / "output"
    folds = read_csv(output / "6-1/fold_accuracy.csv")
    predictions = read_csv(output / "6-1/predictions.csv")
    subjects = read_csv(output / "6-4/subject_metrics.csv")
    fold_f1 = []
    for fold in folds:
        rows = [row for row in predictions if row["fold"] == fold["fold"]]
        fold_f1.append(f1_score([row["true_label"] for row in rows],
                                [row["predicted_label"] for row in rows],
                                labels=("walk", "jump", "squat"), average="macro", zero_division=0))

    metrics = (
        ("Accuracy", [float(row["accuracy"]) for row in folds],
         [float(row["accuracy"]) for row in subjects]),
        ("Macro F1", fold_f1, [float(row["macro_f1"]) for row in subjects]),
    )
    fold_x = list(range(len(folds)))
    subject_x = list(range(len(folds) + 1, len(folds) + 1 + len(subjects)))
    ticks = [f"F{row['fold']}" for row in folds] + [f"S{row['test_subject_id']}" for row in subjects]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), sharey=True, layout="constrained")
    fig.suptitle("Same person, held-out trial vs. held-out person")
    for ax, (title, fold_values, subject_values) in zip(axes, metrics):
        for xs, values, color, marker in ((fold_x, fold_values, "#0072B2", "o"),
                                           (subject_x, subject_values, "#D55E00", "s")):
            ax.scatter(xs, values, color=color, marker=marker, s=55, zorder=3)
            ax.hlines(mean(values), xs[0] - 0.28, xs[-1] + 0.28, color=color,
                      linestyle="--", linewidth=1.5)
        ax.set(title=f"{title} | means: {mean(fold_values):.3f} vs. {mean(subject_values):.3f}",
               ylim=(0, 1.02), xlim=(-0.6, subject_x[-1] + 0.6))
        ax.set_xticks(fold_x + subject_x, ticks)
        ax.axvline(len(folds), color="#B0B0B0", linewidth=1)
        ax.grid(axis="y", alpha=0.25)
        low = subject_values.index(min(subject_values))
        ax.annotate(f"{subject_values[low]:.3f}", (subject_x[low], subject_values[low]),
                    xytext=(0, -15), textcoords="offset points", ha="center", color="#993800")
    axes[0].set_ylabel("Score (0 to 1)")
    fig.legend(handles=[Line2D([], [], color="#0072B2", marker="o", linestyle="none", label="6-1: each fold"),
                        Line2D([], [], color="#D55E00", marker="s", linestyle="none", label="6-4: each subject"),
                        Line2D([], [], color="#555555", linestyle="--", label="Mean within each group")],
               loc="outside lower center", ncols=3)
    target = output / "6-4/comparison.png"
    fig.savefig(target, dpi=180)
    plt.close(fig)
    print(target)


if __name__ == "__main__":
    main()
