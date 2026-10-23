# Stata — First University Assignment

This repository contains my **first university assignment in Stata**, completed to become familiar with Stata's syntax and core tools for empirical data analysis.

The exercise uses a dataset about public managers to practice descriptive statistics, missing-data handling, regression, and comparisons between groups.

## What the code does

1. **Mean imputation:** replaces missing income values with the mean of observed incomes.
2. **Regression imputation:** estimates missing incomes using gender, age, education, ministry, and area of birth.
3. **Group comparison:** applies Welch's two-sample t-test to compare imputed incomes for managers below and above the age threshold of 54.5 years.

## Repository contents

- `income_imputation.do` — Stata script for the assignment.

## Dataset availability

**The dataset is intentionally not included in this public repository**, because it contains personal and income-related information and its redistribution has not been authorized or verified.

The script expects a file named `Data_Public Managers.dta`. To run it, you must obtain that dataset from an authorized source and place it in your local working directory alongside the `.do` file. Without the dataset, the code cannot be executed or its results reproduced from this repository alone.

## Running the code

Open Stata, set the working directory to the folder containing the script and your authorized local copy of the dataset, then execute:

```stata
do income_imputation.do
```

No additional Stata packages are required.

## Notes

This is an introductory learning exercise rather than a publication-ready empirical study. Single regression imputation does not account for imputation uncertainty in the final t-test, so inferential results should be interpreted with caution.
