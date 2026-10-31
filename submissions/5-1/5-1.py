"""課題5-1：標準化せず、2特徴量でロジスティック回帰を行う。"""

from common import FEATURES_A, arguments, evaluate, model, read_data, write_summary


def main():
    args = arguments("5-1")
    rows, train, test = read_data(args)
    result = evaluate(model("logistic_regression"), FEATURES_A, rows, train, test,
                      args.output_dir, "logistic_regression", "unscaled")
    write_summary(args.output_dir, [result])


if __name__ == "__main__":
    main()
