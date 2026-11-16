"""Compare TF-IDF text classifiers on a reproducible holdout split."""

import argparse
import json
import platform
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parent


def load_data(path):
    """Validate binary labels and remove repeated texts before splitting."""
    data = pd.read_csv(path)
    required = {"title_text", "fake_news"}
    if not required.issubset(data.columns):
        raise ValueError("CSV must contain title_text and fake_news columns.")
    data = data[["title_text", "fake_news"]].copy()
    if data.isna().any().any():
        raise ValueError("Text and labels must not contain missing values.")
    if not data["title_text"].map(lambda x: isinstance(x, str)).all():
        raise ValueError("title_text must contain strings.")
    key = data["title_text"].str.replace(r"\s+", " ", regex=True).str.strip().str.lower()
    if key.eq("").any():
        raise ValueError("Text must not be empty.")
    if set(data["fake_news"].unique()) != {0, 1}:
        raise ValueError("fake_news must contain both binary labels 0 and 1.")
    if data.groupby(key)["fake_news"].nunique().gt(1).any():
        raise ValueError("Identical normalized texts have conflicting labels.")
    data["fake_news"] = data["fake_news"].astype(int)
    data["source_row"] = np.arange(len(data))
    keep = ~key.duplicated()
    removed = int((~keep).sum())
    return data.loc[keep].copy(), removed


def evaluate(model, texts, labels):
    predictions = model.predict(texts)
    if hasattr(model, "decision_function"):
        scores = model.decision_function(texts)
    else:
        classes = list(model.classes_)
        scores = model.predict_proba(texts)[:, classes.index(1)]
    return {
        "accuracy": float(accuracy_score(labels, predictions)),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(labels, scores)),
    }, predictions


def save_features(pipeline, name, output):
    """Use the fitted winning model, retaining its tuned parameters."""
    classifier = pipeline.named_steps["classifier"]
    terms = pipeline.named_steps["tfidf"].get_feature_names_out()
    if hasattr(classifier, "coef_"):
        weights = classifier.coef_.ravel()
        description = "Coefficient (positive supports label 1)"
    else:
        weights = classifier.feature_log_prob_[1] - classifier.feature_log_prob_[0]
        description = "Log-probability difference (label 1 minus label 0)"
    indices = np.argsort(np.abs(weights))[::-1][:20]
    table = pd.DataFrame({"term": terms[indices], "weight": weights[indices]})
    table["abs_weight"] = table["weight"].abs()
    table.to_csv(output / "top20_feature_importance.csv", index=False)
    plot = table.sort_values("weight")
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.barh(plot["term"], plot["weight"], color=np.where(plot["weight"] >= 0, "#237b8e", "#cb7046"))
    ax.axvline(0, color="black", linewidth=0.7)
    ax.set(xlabel=description, title=f"Top 20 terms: {name}")
    fig.tight_layout()
    fig.savefig(output / "top20_feature_importance.png", dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "fake_news_train.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if not 0 < args.test_size < 1:
        parser.error("--test-size must be between 0 and 1.")
    data, duplicates = load_data(args.data)
    train, test = train_test_split(
        data, test_size=args.test_size, stratify=data["fake_news"], random_state=args.seed
    )
    if train["fake_news"].value_counts().min() < 5:
        raise ValueError("Training requires at least five examples of each class for 5-fold CV.")
    if test["fake_news"].nunique() != 2:
        raise ValueError("The test split must contain both classes.")
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    print(f"Rows: {len(data)}; duplicates removed: {duplicates}; train: {len(train)}; test: {len(test)}", flush=True)
    split = pd.concat([train.assign(split="train"), test.assign(split="test")])
    split[["source_row", "fake_news", "split"]].sort_values("source_row").to_csv(output / "split_assignments.csv", index=False)

    models = {
        "LinearSVC": (LinearSVC(random_state=args.seed, max_iter=10000), {"classifier__C": [0.1, 1.0, 3.0]}),
        "LogisticRegression": (
            LogisticRegression(solver="liblinear", max_iter=5000, random_state=args.seed),
            {"classifier__C": [0.1, 1.0, 3.0]},
        ),
        "MultinomialNB": (MultinomialNB(), {"classifier__alpha": [0.01, 0.1, 1.0]}),
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=args.seed)
    searches = {}
    rows = []
    for name, (estimator, grid) in models.items():
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                stop_words="english", lowercase=True, ngram_range=(1, 2),
                min_df=2, max_df=0.90, sublinear_tf=True,
            )),
            ("classifier", estimator),
        ])
        search = GridSearchCV(pipeline, grid, scoring="f1", cv=cv, refit=True, error_score="raise")
        search.fit(train["title_text"], train["fake_news"])
        searches[name] = search
        rows.append({"model": name, "cv_f1_mean": float(search.best_score_),
                     "cv_f1_std": float(search.cv_results_["std_test_score"][search.best_index_]),
                     "best_params": json.dumps(search.best_params_, sort_keys=True)})
        pd.DataFrame(search.cv_results_).to_csv(output / f"{name}_cv_results.csv", index=False)
        print(f"{name}: CV F1 = {search.best_score_:.4f}; {search.best_params_}", flush=True)

    # Choose the winner before looking at any held-out test metrics.
    winner = max(rows, key=lambda row: row["cv_f1_mean"])["model"]
    for row in rows:
        name = row["model"]
        fitted = searches[name].best_estimator_
        metrics, predictions = evaluate(fitted, test["title_text"], test["fake_news"])
        row.update({f"test_{key}": value for key, value in metrics.items()})
        row["selected_by_cv"] = name == winner
        report = classification_report(test["fake_news"], predictions, labels=[0, 1], output_dict=True, zero_division=0)
        pd.DataFrame(report).T.to_csv(output / f"{name}_classification_report.csv")
        cm = confusion_matrix(test["fake_news"], predictions, labels=[0, 1])
        pd.DataFrame(cm, index=["true_0", "true_1"], columns=["pred_0", "pred_1"]).to_csv(output / f"{name}_confusion_matrix.csv")
    comparison = pd.DataFrame(rows).sort_values("cv_f1_mean", ascending=False)
    comparison.to_csv(output / "model_comparison.csv", index=False)
    ax = comparison.set_index("model")[["cv_f1_mean", "test_f1"]].plot.bar(
        figsize=(8, 5), color=["#237b8e", "#cb7046"], rot=0
    )
    ax.set(ylabel="F1 (positive label: 1)", ylim=(0, 1.05), title="Model comparison")
    ax.legend(["Cross-validation", "Held-out test"])
    ax.figure.tight_layout()
    ax.figure.savefig(output / "model_f1_comparison.png", dpi=160)
    plt.close(ax.figure)

    best = searches[winner].best_estimator_
    vocabulary_size = len(best.named_steps["tfidf"].vocabulary_)
    (output / "vocabulary_size.txt").write_text(str(vocabulary_size) + "\n", encoding="utf-8")
    save_features(best, winner, output)
    metadata = {
        "input_rows": len(data) + duplicates, "duplicate_rows_removed": duplicates,
        "training_rows": len(train), "test_rows": len(test),
        "seed": args.seed, "test_fraction": args.test_size,
        "cv_folds": 5, "selection_metric": "mean validation F1 for label 1",
        "selected_model": winner, "best_params": searches[winner].best_params_,
        "vocabulary_size": vocabulary_size,
        "train_class_counts": train["fake_news"].value_counts().sort_index().to_dict(),
        "test_class_counts": test["fake_news"].value_counts().sort_index().to_dict(),
        "versions": {"python": platform.python_version(), "scikit-learn": sklearn.__version__,
                     "pandas": pd.__version__, "numpy": np.__version__, "matplotlib": matplotlib.__version__},
    }
    (output / "run_summary.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Selected by CV: {winner}; vocabulary: {vocabulary_size}")
    print(comparison[["model", "cv_f1_mean", "test_f1", "test_accuracy"]].to_string(index=False))
    print(f"Results saved to {output}")


if __name__ == "__main__":
    main()
