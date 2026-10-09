# 第2回：データ取得

## 課題2-3

標準ライブラリの `csv` を使って各CSVを読み込み、データの行数と列数を表示します。
行数にはヘッダーを含めません。追加ライブラリのインストールは不要です。

リポジトリのルートで実行します。

```powershell
python lessons/02-data-collection/2-3.py
```

別のフォルダのCSVを読み込む場合は、フォルダのパスを指定します。

```powershell
python lessons/02-data-collection/2-3.py "C:/path/to/csv-folder"
```

提出用のプログラムは `submissions/2-3.py` に保存しています。

## 課題2-4

元のCSVの右端に `label` 列を追加します。ファイル名から動作を判定し、
各行に `walk`・`jump`・`squat` のいずれかを付けます。
標準ライブラリのみを使います。

リポジトリのルートで実行します。

```powershell
python lessons/02-data-collection/2-4.py
```

元データは変更せず、結果を `data/processed/02-data-collection/` に保存します。
入力・出力フォルダを指定する場合は、次のように実行します。

```powershell
python lessons/02-data-collection/2-4.py "C:/path/to/raw" "C:/path/to/labeled"
```

提出用プログラムは `submissions/2-4.py`、ラベル付きCSVは
`submissions/2-4/` に保存しています。
