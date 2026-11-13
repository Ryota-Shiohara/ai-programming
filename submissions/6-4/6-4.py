"""課題6-4：共有ZIPを直接読み、Subject単位の交差検証を行う。"""

import argparse
import csv
import io
from pathlib import Path, PurePosixPath
import re
from zipfile import ZipFile

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


LABELS = ("walk", "jump", "squat")
SAMPLE_RATE = 30
WINDOW = 30
STEP = 15


def read_subject(path):
    subject = re.fullmatch(r"subject(\d+)\.zip", path.name, flags=re.IGNORECASE)
    if not subject:
        raise ValueError(f"subject番号.zip の形式で指定してください: {path.name}")
    seen, features, labels = set(), [], []
    gaps = 0
    with ZipFile(path) as archive:
        for member in archive.infolist():
            trial = re.fullmatch(r"(walk|jump|squat)_?([1-5])\.csv",
                                 PurePosixPath(member.filename).name, flags=re.IGNORECASE)
            if trial is None:
                continue
            action, number = trial[1].lower(), int(trial[2])
            if (action, number) in seen:
                raise ValueError(f"同じ試行が複数あります: {path.name}, {action}{number}")
            seen.add((action, number))
            # 必要な時刻・加速度だけを読み、共有データを展開・保存しない。
            with archive.open(member) as stream:
                reader = csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig", newline=""))
                samples = [(int(row["timestamp_us"]), *(float(row[f"acc_{axis}"]) for axis in "xyz"))
                           for row in reader]
            data = np.asarray(samples)
            if len(data) < WINDOW or not np.isfinite(data).all():
                raise ValueError(f"試行が短すぎるか値が不正です: {path.name}, {action}{number}")
            intervals = np.diff(data[:, 0]) / 1_000_000
            if np.any(intervals <= 0) or abs(np.median(intervals) - 1 / SAMPLE_RATE) > 0.003:
                raise ValueError(f"約30Hzの時刻順データではありません: {path.name}, {action}{number}")
            breaks = np.flatnonzero(intervals >= 2 / SAMPLE_RATE) + 1
            gaps += len(breaks)
            magnitude = np.sqrt(np.sum(data[:, 1:] ** 2, axis=1))
            before = len(features)
            for segment in np.split(magnitude, breaks):
                for start in range(0, len(segment) - WINDOW + 1, STEP):
                    window = segment[start:start + WINDOW]
                    features.append((float(window.std(ddof=0)), float(window.max())))
                    labels.append(action)
            if len(features) == before:
                raise ValueError(f"連続した30点がありません: {path.name}, {action}{number}")
    if seen != {(a, i) for a in LABELS for i in range(1, 6)}:
        raise ValueError(f"各動作5試行が必要です: {path.name}")
    subject_id = subject[1]
    print(f"Subject {subject_id}: {len(seen)} trials, {len(features)} windows, {gaps} gaps")
    return subject_id, np.asarray(features), np.asarray(labels)


def write_csv(path, header, rows):
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archives", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("lessons/06-evaluation/output/6-4"))
    args = parser.parse_args()
    if len(args.archives) < 3:
        parser.error("解析前に選んだ3名以上のZIPを指定してください。")
    subjects = sorted((read_subject(path) for path in args.archives), key=lambda s: s[0])
    if len({sid for sid, _, _ in subjects}) != len(subjects):
        parser.error("同じSubjectが複数指定されています。")

    metrics, class_counts = [], []
    for test_id, x_test, y_test in subjects:
        train = [(sid, x, y) for sid, x, y in subjects if sid != test_id]
        x_train = np.concatenate([x for _, x, _ in train])
        y_train = np.concatenate([y for _, _, y in train])
        # 6-1と同じ2特徴量・標準化・ロジスティック回帰。
        # 標準化もモデルも評価対象者を一切含まないデータでfitする。
        model = make_pipeline(StandardScaler(), LogisticRegression(
            C=1.0, solver="lbfgs", max_iter=10000, random_state=42))
        model.fit(x_train, y_train)
        predicted = model.predict(x_test)
        correct = int(np.count_nonzero(predicted == y_test))
        accuracy = correct / len(y_test)
        macro_f1 = f1_score(y_test, predicted, labels=LABELS, average="macro", zero_division=0)
        metrics.append((test_id, ";".join(sid for sid, _, _ in train),
                        len(y_train), len(y_test), correct, accuracy, macro_f1))
        matrix = confusion_matrix(y_test, predicted, labels=LABELS)
        class_counts.extend((test_id, label, *row) for label, row in zip(LABELS, matrix))
        print(f"Subject {test_id}: accuracy={accuracy:.4%}, macro F1={macro_f1:.6f}")

    values = np.asarray([row[-2:] for row in metrics])
    means, stds = values.mean(axis=0), values.std(axis=0, ddof=0)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "subject_metrics.csv",
              ("test_subject_id", "train_subject_ids", "train_windows", "test_windows",
               "correct", "accuracy", "macro_f1"), metrics)
    write_csv(args.output_dir / "metrics_summary.csv", ("metric", "subjects", "mean", "std_ddof_0"),
              [(name, len(subjects), mean, std) for name, mean, std in
               zip(("accuracy", "macro_f1"), means, stds)])
    write_csv(args.output_dir / "subject_confusion_counts.csv", ("subject_id", "true_label", *LABELS),
              class_counts)


if __name__ == "__main__":
    main()
