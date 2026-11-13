# 第6回：検証

リポジトリのルートから順に実行します。第5回と同じ仮想環境を使用します。

```powershell
.\.venv\Scripts\python.exe lessons/06-evaluation/6-1.py
.\.venv\Scripts\python.exe lessons/06-evaluation/6-2.py
.\.venv\Scripts\python.exe lessons/06-evaluation/6-3.py
.\.venv\Scripts\python.exe lessons/06-evaluation/package_submissions.py
```

- 6-1は第5回の特徴量表から標準偏差・最大値を使う。Fold nでは各動作の試行nを評価に使い、残る12試行で標準化とロジスティック回帰を学習する。全331窓を一度ずつ評価し、各窓の正解・予測・クラス別確率を保存する。平均と標準偏差（ddof=0）は5つのFold Accuracyを同じ重みで集計する。
- 6-2は6-1の評価予測を結合する。混同行列は行が真値、列が予測。割合は真値クラスごとの行和で割る。全窓AccuracyはFold Accuracyの単純平均とは集計方法が異なる。
- 6-3は同じ予測結果からJump確率を取り出し、Jumpを陽性、WalkとSquatを陰性としてROCとAUCを計算する。再学習や評価窓に基づく閾値選択は行わない。
- 図とCSVは `output/6-1/`〜`output/6-3/` に保存される。各コードは入力パスと `--output-dir` を指定できる。6-2と6-3の入力は6-1の `predictions.csv`。

## 考察と提出

各 `submissions/6-x/README.md` の考察欄を本人の観察に基づいて埋める。`package_submissions.py` は結果とコードを準備し、考察を記入した課題のみZIPにする。

## 6-4：未知のSubjectへの評価

解析前にSubject 03・05・06を選び、選定理由・取得条件は `submissions/6-4/README.md` に記録した。Subject単位で評価用の1名を外し、残りのSubjectだけで標準化と学習を行う。平均と標準偏差（ddof=0）はSubjectを等しく重み付けして計算する。

共有ZIPをリポジトリの外に置き、ファイルパスを指定する。コードはZIPを直接読み、元データや窓ごとのデータを保存しない。

```powershell
.\.venv\Scripts\python.exe lessons/06-evaluation/6-4.py "C:/path/to/subject03.zip" "C:/path/to/subject05.zip" "C:/path/to/subject06.zip"
```

取得時刻の途切れは区間を分けて処理し、区間内で6-1と同じ30サンプル窓・15サンプル刻み・2特徴量を使う。`output/6-4/` には集計だけを保存する。
