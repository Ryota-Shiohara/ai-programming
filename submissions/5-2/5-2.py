"""課題5-2：同じ分割・モデルで標準化の有無を比較する。"""

from common import FEATURES_A, arguments, evaluate, model, read_data, write_scaler, write_summary


def main():
    args = arguments("5-2")
    rows, train, test = read_data(args)
    results = []
    for standardize, name in ((False, "unscaled"), (True, "scaled")):
        estimator = model("logistic_regression", standardize)
        results.append(evaluate(estimator, FEATURES_A, rows, train, test,
                                args.output_dir, "logistic_regression", name))
        if standardize:
            write_scaler(args.output_dir, estimator, FEATURES_A, name)
    write_summary(args.output_dir, results)


if __name__ == "__main__":
    main()
