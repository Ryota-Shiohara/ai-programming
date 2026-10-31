"""第5回の学習結果と記入済みREADMEを提出用ZIPにまとめる。"""

from pathlib import Path
from shutil import copyfile
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    root = Path(__file__).resolve().parents[2]
    lesson = root / "lessons/05-machine-learning"
    data = root / "data/processed/05-machine-learning"
    for task in ("5-1", "5-2", "5-3", "5-4"):
        folder = root / "submissions" / task
        folder.mkdir(parents=True, exist_ok=True)
        for source in (lesson / f"{task}.py", lesson / "common.py", lesson / "事前予想.md",
                       data / "features.csv", data / "split.csv"):
            copyfile(source, folder / source.name)
        if task == "5-1":
            copyfile(lesson / "output/5-1.png", folder / "5-1.png")
            copyfile(lesson / "prepare.py", folder / "prepare.py")
        if task == "5-4":
            copyfile(lesson / "feature_definitions.csv", folder / "feature_definitions.csv")
        result_dir = lesson / "output" / task
        if not (result_dir / "accuracy.csv").exists():
            print(f"{task}: 学習未実行。コード・データ・分割は準備済みです。")
            continue
        for source in sorted(result_dir.iterdir()):
            if source.is_file():
                copyfile(source, folder / source.name)
        readme = folder / "README.md"
        if "【未記入】" in readme.read_text(encoding="utf-8"):
            print(f"{task}: READMEの記入待ちです。")
            continue
        files = [path for path in sorted(folder.iterdir()) if path.is_file()]
        target = root / "submissions" / f"{task}.zip"
        with ZipFile(target, "w", ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, path.name)
        with ZipFile(target) as archive:
            assert archive.testzip() is None
            for path in files:
                assert archive.read(path.name) == path.read_bytes()
        print(f"{task}.zip: 作成・確認済み")


if __name__ == "__main__":
    main()
