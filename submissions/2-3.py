"""課題2-3：各CSVのデータ行数（ヘッダーを除く）と列数を表示する。"""

import argparse
import csv
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "data_dir",
        nargs="?",
        type=Path,
        default=Path("data/raw/02-data-collection"),
        help="CSVが入ったフォルダ（省略時はリポジトリのルートから実行）",
    )
    args = parser.parse_args()
    files = sorted(args.data_dir.glob("*.csv"))
    if not files:
        parser.error(f"CSVファイルが見つかりません: {args.data_dir}")

    print("データ行数はヘッダーを除いて数えます。")
    for path in files:
        with path.open(encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)
            header = next(reader)
            rows = sum(1 for row in reader if row)
        print(f"{path.name}: {rows}行 × {len(header)}列")


if __name__ == "__main__":
    main()
