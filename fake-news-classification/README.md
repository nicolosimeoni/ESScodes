# Fake News Text Classification

Compare Linear SVM, Logistic Regression and Multinomial Naive Bayes using TF-IDF and five-fold cross-validation.

## Run

Python 3.11 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python fake_news_classifier.py
```

On Windows, activate with `.venv\Scripts\activate`.

The dataset is included in `data/fake_news_train.csv`. The script removes repeated texts and creates a stratified 80/20 train/test split with seed 42. TF-IDF is fitted inside each validation fold; the winner is chosen by validation F1.

Metrics and charts are generated in `results/` when the script runs. Generated results are excluded from this package and ignored by Git.

The original test set is unavailable, so this split does not reproduce the original assignment evaluation. This is a text classification exercise, not an independent fact-checking tool. Data provenance and the original labeling guide were not supplied; label 1 is treated as the positive class.
