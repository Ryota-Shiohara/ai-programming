# データ

- `raw/`：センサから取得した元のCSV。加工せずに保存する。
- `processed/`：ラベル付与・前処理後のCSV。

ファイル名は動作と試行番号がわかる名前にします（例：`walk_01.csv`）。
別の計測セットはサブフォルダに分けます（例：`raw/02-data-collection/`）。

## 計測条件の記録

データを追加したら、計測セットごとに以下を記録してください。

- 計測日時
- 動作の種類・英語ラベル
- 使用した端末・センサ
- サンプリング周波数
- 1試行の記録時間・試行回数
- スマートフォンの装着場所・向き
- 元データと加工後データの対応・加工内容

提出時は必要な計測条件をテキストファイルなどにまとめ、データと一緒に提出します。

## 計測セット

- 第2回（課題2-5）：`raw/02-data-collection-bonus/` に移動・田植え各5試行の元CSVを保存。`processed/02-data-collection-bonus/` に右端の `label` 列へ `move`・`plant` を付与したCSVと提出用READMEを保存。提出用ZIPは `submissions/2-5.zip`。

- 第2回（課題2-2）：`raw/02-data-collection/`。walk・jump・squat各5試行。計測条件は同フォルダの `measurement-conditions.txt` に記録。
- 第2回（課題2-4）：`processed/02-data-collection/`。元のCSVと同じファイル名で保存し、右端の `label` 列にファイル名に対応する英語の動作ラベルを追加。元の32列は保持。
