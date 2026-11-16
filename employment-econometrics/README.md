# Employment, Wages and Capital

An econometrics coursework project studying the relationship between employment, relative wages and capital across four sectors. The analysis uses Stata to estimate OLS models, test sectoral heterogeneity and compare conventional inference with heteroskedasticity-robust standard errors.

**Authors:** Gabriele N, Valentina P and Nicolò Simeoni  
**Course:** Econometrics (20203)

## Analysis

1. Describe the dataset and its sector composition.
2. Estimate a baseline employment equation using wages and capital.
3. Test individual and joint coefficient significance.
4. Examine differences in sector means, intercepts and slopes.
5. Estimate a model with sector indicators and wage/capital interactions.
6. Test conditional homoskedasticity using the White test.
7. Re-estimate with HC1 robust standard errors and repeat sectoral tests.

The fully interacted model allows the intercept and both slopes to differ across sectors, with sector 1 as the reference category. `ys` is constant within each sector; sector indicators are used to accommodate sector differences.

## Data

The supplied coursework dataset contains **3,138 firms**, four sectors and no missing values in the five variables below. Variable descriptions follow the dataset labels.

| Variable | Description |
| --- | --- |
| `n` | Log of employment |
| `w` | Log of relative wage |
| `k` | Log of capital |
| `sector` | Sector code, from 1 to 4 |
| `ys` | Log of sectoral output |

The original data are preserved. External provenance and redistribution terms were not supplied with the assignment.

## Run

Requires **Stata 15.1 or later**. No user-written packages are needed.

From Stata, change to the repository folder and run:

```stata
cd "/path/to/employment-econometrics"
do analysis.do
```

Alternatively, provide the repository folder as a quoted argument:

```stata
do "/path/to/employment-econometrics/analysis.do" "/path/to/employment-econometrics"
```

The script creates `output/analysis.log` with all regression and test output. Each successful rerun replaces the previous log.

## Files

| File | Contents |
| --- | --- |
| [`analysis.do`](analysis.do) | Stata analysis, organised into the seven assignment questions |
| [`data/assignment_data_group_6.dta`](data/assignment_data_group_6.dta) | Original coursework dataset |
| [`report/assignment1_group6.pdf`](report/assignment1_group6.pdf) | Original group report |
| `.gitignore` | Excludes generated output and local editor/system files |

## Main findings

The baseline wage coefficient is **-1.3151**, while the capital coefficient is **0.3621**. The baseline model has a low R-squared (**0.0088**). Sector interactions are jointly significant under conventional inference, and the White test rejects homoskedasticity. Robust standard errors change the significance of several individual coefficients.

These estimates describe associations. Joint significance does not establish that each regressor is individually significant, or diagnose multicollinearity. Interaction coefficients measure differences from sector 1; add the relevant main coefficient to obtain another sector's slope. Robust standard errors address heteroskedasticity in inference but do not resolve endogeneity, misspecification or influential observations. The unusually wide range of `n` is retained as supplied.

The PDF is the original submission. The script adds a joint test of all sector terms and repeats sectoral tests with robust standard errors. Key numerical results were independently checked in Python; the packaged script has not been executed in Stata in the preparation environment.
