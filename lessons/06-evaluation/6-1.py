"""課題6-1：各動作の同番号の試行を評価用にする5分割交差検証。"""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


LABELS = ("walk", "jump", "squat")


def write_csv(path, header, rows):
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("features", nargs="?", type=Path,
                        default=Path("data/processed/05-machine-learning/features.csv"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("lessons/06-evaluation/output/6-1"))
    args = parser.parse_args()
    with args.features.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    expected = {f"{label}{n}": label for label in LABELS for n in range(1, 6)}
    trials = np.array([row["trial_id"] for row in rows])
    y = np.array([row["label"] for row in rows])
    if set(trials) != set(expected) or any(expected[t] != label for t, label in zip(trials, y)):
        raise ValueError("各動作の5試行と対応するラベルが必要です。")
    if len({(r["trial_id"], r["window_id"]) for r in rows}) != len(rows):
        raise ValueError("同じ試行・窓番号が重複しています。")
    x = np.array([[float(row["std"]), float(row["max"])] for row in rows])
    if not np.isfinite(x).all():
        raise ValueError("特徴量に非有限値があります。")

    predictions, fold_results = [], []
    for fold in range(1, 6):
        test_ids = [f"{label}{fold}" for label in LABELS]
        test = np.isin(trials, test_ids)
        train = ~test
        # fitは各Foldの学習用データだけ。標準化もその中で行う。
        model = make_pipeline(StandardScaler(), LogisticRegression(
            C=1.0, solver="lbfgs", max_iter=10000, random_state=42))
        model.fit(x[train], y[train])
        predicted = model.predict(x[test])
        probabilities = model.predict_proba(x[test])
        order = [list(model.classes_).index(label) for label in LABELS]
        correct = int(np.count_nonzero(predicted == y[test]))
        accuracy = correct / int(test.sum())
        fold_results.append((fold, ";".join(sorted(set(trials[train]))),
                             ";".join(test_ids), int(train.sum()), int(test.sum()), correct, accuracy))
        for index, label, prob in zip(np.flatnonzero(test), predicted, probabilities[:, order]):
            predictions.append((fold, trials[index], rows[index]["window_id"], y[index], label, *prob))

    accuracies = np.array([row[-1] for row in fold_results])
    mean, std = float(accuracies.mean()), float(accuracies.std(ddof=0))
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "fold_accuracy.csv",
              ("fold", "train_trial_ids", "test_trial_ids", "train_windows", "test_windows", "correct", "accuracy"),
              fold_results)
    write_csv(out / "accuracy_summary.csv", ("folds", "mean_accuracy", "std_accuracy_ddof_0"),
              [(len(accuracies), mean, std)])
    write_csv(out / "predictions.csv",
              ("fold", "trial_id", "window_id", "true_label", "predicted_label", *[f"prob_{label}" for label in LABELS]),
              predictions)
    fig, ax = plt.subplots(figsize=(7.2, 4.2), layout="constrained")
    bars = ax.bar(range(1, 6), accuracies * 100, color="#0072B2")
    ax.axhline(mean * 100, color="#D55E00", linestyle="--", label=f"Mean: {mean:.1%}")
    ax.bar_label(bars, fmt="%.1f%%", padding=3,
                 bbox={"facecolor": "white", "edgecolor": "none", "pad": 1})
    ax.set(title="Accuracy by held-out trial number", xlabel="Fold", ylabel="Accuracy [%]",
           xticks=range(1, 6), ylim=(0, 108))
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right")
    fig.savefig(out / "fold_accuracy.png", dpi=180)
    plt.close(fig)
    print(f"Fold accuracy: {accuracies}; mean={mean:.4%}, std={std:.4%}")


if __name__ == "__main__":
    main()
