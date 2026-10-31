"""課題5-3：ロジスティック回帰・決定木・ランダムフォレスト・XGBoostを比較する。"""

from common import FEATURES_A, arguments, evaluate, model, read_data, write_summary


def main():
    args = arguments("5-3")
    rows, train, test = read_data(args)
    results = []
    for name in ("logistic_regression", "decision_tree", "random_forest", "xgboost"):
        # ロジスティック回帰は5-2と同じ標準化。木モデルは標準化しない。
        estimator = model(name, standardized=name == "logistic_regression")
        results.append(evaluate(estimator, FEATURES_A, rows, train, test,
                                args.output_dir, name, name))
    write_summary(args.output_dir, results)


if __name__ == "__main__":
    main()
