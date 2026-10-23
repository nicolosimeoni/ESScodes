use "Data_Public Managers.dta", clear

summ income if income < ., meanonly
gen double income_meanimp = income
replace income_meanimp = r(mean) if missing(income_meanimp)
summ income_meanimp
display "A1  Mean (mean-imp): " %12.2f r(mean)
display "A1  SD:              " %12.4f r(sd)

* (2) Regression-imputation

encode min, gen(min_cat)

regress income gender age i.level_edu i.min_cat i.areaofbirth if income < .

predict double yhat
gen double income_regimp = income
replace income_regimp = yhat if missing(income_regimp) & yhat < .
summ income_regimp
display "A2  Mean (reg-imp):  " %12.2f r(mean)
display "A2  SD:              " %12.4f r(sd)

* (3) Mean difference between <54.5 and ≥54.5 (Welch) about income_regimp
gen byte agegrp = (age >= 54.5) if age < . & income_regimp < .
ttest income_regimp, by(agegrp) unequal
local diff = r(mu_2) - r(mu_1)
display "A3  Diff (>=54.5 - <54.5): " %12.2f `diff' "   p(two-sided): " %10.4g r(p)
