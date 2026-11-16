# Econometrics Assignment 2

Time-series analysis and inflation forecasting in R, written as a Quarto document.

The assignment explores stationarity and structural breaks, ARIMA models, random walks with and without drift, unconditional mean forecasts, ARDL models, and an AR(2) benchmark.

## Files

- `WIP_Assignment_Econometrics_2.qmd`: original R code and document structure.
- `final_dataset.csv`: annual macroeconomic data for 1990–2025. The models use subsets of these observations.

## Requirements

R and Quarto, with the following R packages:

```r
install.packages(c(
  "forecast", "tseries", "foreign", "readxl", "ggplot2",
  "strucchange", "vars", "dplyr", "tibble", "readr",
  "ARDL", "FinTS", "moments", "knitr", "xtable", "rmarkdown"
))
```

## Run

The original source is preserved unchanged, including its machine-specific input path:

```r
final_dataset <- read_csv("C:/Users/Stealth/Downloads/final_dataset.csv")
```

Before running on another computer, update that line in your local copy to point to the included dataset. With both files in the same directory, use:

```r
final_dataset <- read_csv("final_dataset.csv")
```

From the repository directory, render the HTML report with:

```bash
quarto render WIP_Assignment_Econometrics_2.qmd
```

Alternatively, open the `.qmd` file in RStudio and click **Render**.

## Status

Academic work in progress. The supplied code and dataset are unchanged; this repository packages them for sharing. The full analysis has not been executed or independently validated as part of this packaging.
