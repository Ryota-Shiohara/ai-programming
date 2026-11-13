"""第6回の提出ファイルを揃え、考察を記入した課題だけZIPにする。"""

from pathlib import Path
from shutil import copyfile
from zipfile import ZIP_DEFLATED, ZipFile


OUTPUT_FILES = {
    "6-1": ("fold_accuracy.csv", "accuracy_summary.csv", "predictions.csv", "fold_accuracy.png"),
    "6-2": ("confusion_counts.csv", "confusion_true_class_rates.csv", "confusion.png",
            "class_metrics.csv", "overall_metrics.csv"),
    "6-3": ("roc.png", "auc.csv"),
    "6-4": ("subject_metrics.csv", "metrics_summary.csv"),
}


def main():
    lesson = Path(__file__).resolve().parent
    submissions = lesson.parents[1] / "submissions"
    for task, names in OUTPUT_FILES.items():
        folder = submissions / task
        code = folder / f"{task}.py"
        copyfile(lesson / code.name, code)
        for name in names:
            copyfile(lesson / "output" / task / name, folder / name)
        readme = folder / "README.md"
        if "【未記入】" in readme.read_text(encoding="utf-8"):
            print(f"{task}: 考察の記入待ち")
            continue
        files = [code, readme, *(folder / name for name in names)]
        target = submissions / f"{task}.zip"
        with ZipFile(target, "w", ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, path.name)
        with ZipFile(target) as archive:
            assert archive.testzip() is None
            assert set(archive.namelist()) == {path.name for path in files}
            assert all(archive.read(path.name) == path.read_bytes() for path in files)
        print(f"{target.name}: 作成・確認済み")


if __name__ == "__main__":
    main()
