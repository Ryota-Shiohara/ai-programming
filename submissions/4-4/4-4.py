"""課題4-4：合成加速度の標準偏差とRMSまたは最大値を散布図で比較する。"""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("features_csv", nargs="?", type=Path,
                        default=Path("data/processed/04-preprocessing/features.csv"))
    parser.add_argument("--output", type=Path,
                        help="出力画像のパス（省略時は特徴量に応じた名前で保存）")
    parser.add_argument("--y-feature", choices=("rms", "max"), default="max",
                        help="縦軸の特徴量（既定はmax）")
    args = parser.parse_args()
    feature_name = {"rms": "RMS", "max": "Maximum"}[args.y_feature]
    if args.output is None:
        filename = "4-4.png" if args.y_feature == "max" else "4-4-std-rms.png"
        args.output = Path("lessons/04-preprocessing/output") / filename
    with args.features_csv.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    if {row["label"] for row in rows} != {"walk", "jump", "squat"}:
        raise ValueError("比較する3動作が揃っていません。4-2.py --allで処理してください。")
    fig, ax = plt.subplots(figsize=(8.5, 6), layout="constrained")
    for action, color, marker in zip(("walk", "jump", "squat"),
                                    ("#0072B2", "#D55E00", "#009E73"), ("o", "^", "s")):
        points = np.array([[float(row["std"]), float(row[args.y_feature])]
                           for row in rows if row["label"] == action])
        if not np.isfinite(points).all():
            raise ValueError("特徴量に欠損・非有限値があります。")
        ax.scatter(points[:, 0], points[:, 1], label=f"{action.capitalize()} (n={len(points)})",
                   color=color, marker=marker, s=28, alpha=0.65, edgecolors="none")
    ax.set(title=f"Window features: standard deviation vs {feature_name}\n1-second windows, 50% overlap; gravity-removed acceleration magnitude",
           xlabel="Standard deviation [m/s²]", ylabel=f"{feature_name} [m/s²]", xlim=(0, None), ylim=(0, None))
    ax.legend()
    ax.grid(alpha=0.25)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=180)
    plt.close(fig)
    print(f"Saved: {args.output}; each point represents one window")


if __name__ == "__main__":
    main()
