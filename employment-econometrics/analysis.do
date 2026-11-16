/*
    Employment, Wages and Capital
    Econometrics (20203) - Assignment 1, Group 6
    Authors: Gabriele Nespoli, Valentina Piardi, Nicolò Simeoni

    Run from the repository root: do analysis.do
    Or pass the repository root as one quoted argument.
    Requires Stata 15.1 or later; no user-written packages.
*/

version 15.1
clear all
set more off

args project_root
if `"`project_root'"' != "" {
    cd `"`project_root'"'
}

capture confirm file "data/assignment_data_group_6.dta"
if _rc {
    display as error "Dataset not found. Run from the repository root or pass its path."
    exit 601
}

capture mkdir "output"
capture log close employment_analysis
log using "output/analysis.log", text replace name(employment_analysis)

use "data/assignment_data_group_6.dta", clear

* Check the variables required by the supplied assignment.
foreach variable in sector ys w k n {
    confirm numeric variable `variable'
    assert !missing(`variable')
}
assert inlist(sector, 1, 2, 3, 4)

* Question 1: describe the data.
describe
summarize sector ys w k n
tabulate sector

* Question 2: estimate the baseline employment equation.
regress n w k
estimates store baseline

* Question 3: individual t-tests appear in the regression output.
* Joint null: the wage and capital coefficients are both zero.
test w k

* Question 4: examine sectoral heterogeneity.
* These exploratory regressions test unconditional differences in means.
regress n i.sector
testparm i.sector

regress w i.sector
testparm i.sector

regress k i.sector
testparm i.sector

* Allow sector-specific intercepts and slopes, using sector 1 as the base.
regress n c.w##ib1.sector c.k##ib1.sector

* Full homogeneity null: all sector intercept and slope differences are zero.
testparm i.sector c.w#i.sector c.k#i.sector

* Separate null: wage and capital slopes are equal across sectors.
testparm c.w#i.sector c.k#i.sector

* Question 5: retain the fully interacted specification.
* An interaction coefficient is a slope difference from sector 1.
regress n c.w##ib1.sector c.k##ib1.sector
estimates store sector_ols

* Question 6: White test of conditional homoskedasticity.
* This postestimation test uses the conventional OLS fit above.
estat imtest, white

* Question 7: use HC1 heteroskedasticity-robust standard errors.
* Coefficient estimates are unchanged; inference uses a robust covariance.
regress n c.w##ib1.sector c.k##ib1.sector, vce(robust)
estimates store sector_robust

* Repeat sectoral tests using the robust covariance estimator.
testparm i.sector c.w#i.sector c.k#i.sector
testparm c.w#i.sector c.k#i.sector

* Compare the same coefficients under conventional and robust inference.
estimates table sector_ols sector_robust, b(%10.4f) se(%10.4f) stats(N r2)

log close employment_analysis
