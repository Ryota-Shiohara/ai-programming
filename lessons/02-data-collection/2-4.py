"""課題2-4：CSVの右端に英語の動作ラベルを追加する。"""

import argparse
import csv
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "data_dir", nargs="?", type=Path,
        default=Path("data/raw/02-data-collection"),
        help="元のCSVが入ったフォルダ",
    )
    parser.add_argument(
        "output_dir", nargs="?", type=Path,
        default=Path("data/processed/02-data-collection"),
        help="ラベル付きCSVの保存先",
    )
    args = parser.parse_args()
    if args.data_dir.resolve() == args.output_dir.resolve():
        parser.error("元データと保存先は別のフォルダにしてください。")

    files = sorted(args.data_dir.glob("*.csv"))
    if not files:
        parser.error(f"CSVファイルが見つかりません: {args.data_dir}")

    # ファイル名から動作を判定する（例：walk1.csv → walk）。
    labeled_files = []
    for path in files:
        label = next(
            (action for action in ("walk", "jump", "squat")
             if path.stem.startswith(action)
             and path.stem[len(action):].isdigit()),
            None,
        )
        if label is None:
            parser.error(f"動作ラベルを判定できないファイル名です: {path.name}")
        labeled_files.append((path, label))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for path, label in labeled_files:
        output_path = args.output_dir / path.name
        with path.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.reader(source)
            header = next(reader)
            if "label" in header:
                parser.error(f"すでにlabel列があります: {path.name}")
            with output_path.open("w", encoding="utf-8", newline="") as output:
                writer = csv.writer(output)
                writer.writerow(header + ["label"])
                rows = 0
                for row in reader:
                    if row:
                        writer.writerow(row + [label])
                        rows += 1
        print(f"{path.name}: {label} ({rows}行) -> {output_path}")


if __name__ == "__main__":
    main()
