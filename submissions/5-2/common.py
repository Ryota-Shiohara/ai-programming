"""第5回のデータ検証・試行分割・モデル・結果保存の共通処理。"""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

FEATURES_A = ["std", "max"]
FEATURES_B = ["std", "max", "mean", "fft_peak_hz"]


def arguments(task):
    parser = argparse.ArgumentParser()
    parser.add_argument("features_csv", nargs="?", type=Path,
                        default=Path("data/processed/05-machine-learning/features.csv"))
    parser.add_argument("--split", type=Path,
                        default=Path("data/processed/05-machine-learning/split.csv"))
    parser.add_argument("--predictions-file", type=Path,
                        default=Path("lessons/05-machine-learning/事前予想.md"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("lessons/05-machine-learning/output") / task)
    args = parser.parse_args()
    text = args.predictions_file.read_text(encoding="utf-8")
    required = ["## 5-1：標準偏差・最大値で分類する場合"]
    if task == "5-4":
        required.append("## 5-4：平均・FFTピーク周波数を追加する場合")
    for heading in required:
        section = text.split(heading, 1)[-1].split("\n## ", 1)[0].strip()
        if heading not in text or not section or "【未記入】" in section:
            parser.error(f"事前予想を記入してから学習してください: {heading}")
    return args


def read_data(args):
    with args.features_csv.open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    with args.split.open(encoding="utf-8-sig", newline="") as file:
        split_rows = list(csv.DictReader(file))
    mapping = {row["trial_id"]: row["split"] for row in split_rows}
    expected = {f"{a}{i}": "test" if i == 5 else "train"
                for a in ("walk", "jump", "squat") for i in range(1, 6)}
    if len(split_rows) != 15 or mapping != expected:
        raise ValueError("分割は各動作の1〜4試行目をtrain、5試行目をtestに固定します。")
    if {row["trial_id"] for row in rows} != set(expected):
        raise ValueError("全15試行の特徴量が必要です。")
    keys = {(row["trial_id"], row["window_id"]) for row in rows}
    if len(keys) != len(rows):
        raise ValueError("ウィンドウIDが重複しています。")
    for row in rows:
        if (Path(row["source_file"]).stem != row["trial_id"]
                or row["label"] != row["trial_id"].rstrip("0123456789")):
            raise ValueError("元試行ID・ラベルの対応が不正です。")
    train = np.array([mapping[row["trial_id"]] == "train" for row in rows])
    test = ~train
    assert {row["trial_id"] for row, use in zip(rows, train) if use}.isdisjoint(
        {row["trial_id"] for row, use in zip(rows, test) if use})
    return rows, train, test


def model(name, standardized=False):
    if name == "logistic_regression":
        estimator = LogisticRegression(C=1.0, solver="lbfgs", max_iter=10000, random_state=42)
    elif name == "decision_tree":
        estimator = DecisionTreeClassifier(max_depth=4, min_samples_leaf=2, random_state=42)
    elif name == "random_forest":
        estimator = RandomForestClassifier(n_estimators=200, min_samples_leaf=2,
                                           random_state=42, n_jobs=1)
    elif name == "xgboost":
        from xgboost import XGBClassifier
        estimator = XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.1,
                                  subsample=1.0, colsample_bytree=1.0, reg_lambda=1.0,
                                  objective="multi:softprob", eval_metric="mlogloss",
                                  tree_method="hist", random_state=42, n_jobs=1)
    else:
        raise ValueError(name)
    return make_pipeline(StandardScaler(), estimator) if standardized else estimator


def write_csv(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def evaluate(estimator, features, rows, train, test, output, name, condition):
    x = np.array([[float(row[column]) for column in features] for row in rows])
    y = np.array([row["label"] for row in rows])
    if not np.isfinite(x).all():
        raise ValueError("特徴量に欠損・非有限値があります。")
    # Pipelineの場合もfitは学習用だけ。評価用から標準化パラメータを求めない。
    label_encoder = None
    if name == "xgboost":
        # XGBoostは0始まりの整数ラベルを要求するため、学習用だけで対応を作る。
        label_encoder = LabelEncoder().fit(y[train])
        estimator.fit(x[train], label_encoder.transform(y[train]))
        pred_train = label_encoder.inverse_transform(estimator.predict(x[train]).astype(int))
        pred_test = label_encoder.inverse_transform(estimator.predict(x[test]).astype(int))
    else:
        estimator.fit(x[train], y[train])
        pred_train = estimator.predict(x[train])
        pred_test = estimator.predict(x[test])
    prediction_rows = [dict(trial_id=row["trial_id"], source_file=row["source_file"],
                            window_id=row["window_id"], true_label=row["label"],
                            predicted_label=str(prediction), correct=int(prediction == row["label"]))
                       for row, prediction in zip([r for r, use in zip(rows, test) if use], pred_test)]
    write_csv(output / f"predictions-{condition}.csv",
              ["trial_id", "source_file", "window_id", "true_label", "predicted_label", "correct"], prediction_rows)
    settings = dict(model=name, condition=condition, features=features,
                    parameters=estimator.get_params(deep=True))
    if label_encoder is not None:
        settings["label_mapping"] = {str(i): str(label) for i, label in enumerate(label_encoder.classes_)}
    output.mkdir(parents=True, exist_ok=True)
    (output / f"settings-{condition}.json").write_text(
        json.dumps(settings, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    summary = dict(model=name, condition=condition, features=";".join(features),
                   train_windows=int(train.sum()), test_windows=int(test.sum()),
                   train_accuracy=float(accuracy_score(y[train], pred_train)),
                   test_accuracy=float(accuracy_score(y[test], pred_test)),
                   test_correct=int(np.sum(y[test] == pred_test)))
    print(summary)
    return summary


def write_summary(output, summaries):
    write_csv(output / "accuracy.csv", list(summaries[0]), summaries)


def write_scaler(output, estimator, features, name):
    scaler = estimator.named_steps["standardscaler"]
    rows = [dict(feature=feature, train_mean=float(mean), train_std=float(np.sqrt(variance)),
                 applied_scale=float(scale))
            for feature, mean, variance, scale in zip(features, scaler.mean_, scaler.var_, scaler.scale_)]
    write_csv(output / f"scaler-{name}.csv", list(rows[0]), rows)
