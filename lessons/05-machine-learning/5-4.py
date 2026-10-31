"""課題5-4：標準化付きロジスティック回帰に固定し、2特徴量と4特徴量を比較する。"""

from common import (FEATURES_A, FEATURES_B, arguments, evaluate, model,
                    read_data, write_scaler, write_summary)


def main():
    args = arguments("5-4")
    rows, train, test = read_data(args)
    results = []
    for features, condition in ((FEATURES_A, "A"), (FEATURES_B, "B")):
        estimator = model("logistic_regression", standardized=True)
        results.append(evaluate(estimator, features, rows, train, test,
                                args.output_dir, "logistic_regression", condition))
        write_scaler(args.output_dir, estimator, features, condition)
    write_summary(args.output_dir, results)


if __name__ == "__main__":
    main()
