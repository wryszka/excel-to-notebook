# Excel to SQL: the mapping

Two tables. The first maps Excel formulas to SQL. The second maps each tab of the loss trend workbook to its notebook and table.

## Formula to SQL

| In Excel | In SQL | Where to see it |
|---|---|---|
| A tab of pasted data | A table | `simple_101`, step 2 |
| A row formula, `=C2+D2`, filled down | An expression on columns: `paid + outstanding` | `simple_101`, step 3 |
| `=SUMIFS(values, keys, A2)` for each row of a summary | `sum(value) ... GROUP BY key` | `simple_101`, step 3 |
| `=COUNTIFS(keys, A2)` | `count(*) ... GROUP BY key` | `simple_101`, step 3 |
| `=VLOOKUP(A2, other_tab, 2, FALSE)` | `JOIN other_table USING (key)` | `simple_101`, step 3 |
| `=C2/D2` | `incurred / earned_premium` | `simple_101`, step 3 |
| A triangle of `SUMIFS(..., age, "<=" & column)` | A join on `age <= column age`, then `sum` | `2_triangles` |
| A triangle laid out as a grid | `PIVOT (... FOR age IN (12, 24, ...))` | `2_triangles` |
| Age-to-age factor, `=SUM(next column)/SUM(this column)` | The triangle joined to itself on `age + 12`, then `sum(next) / sum(this)` | `3_development_factors`, step 1 |
| A yellow input cell | A row in a selection table, with who, when and why | `3_development_factors`, step 2 |
| `=PRODUCT(range)` | `exp(sum(ln(value)))` | `3_development_factors`, step 3 |
| `=LOGEST(values, years) - 1` | `exp(regr_slope(ln(value), year)) - 1` | `4_trend`, step 2 |
| Yellow assumption cells | One small `assumptions` view at the top of the notebook | `1_indication` |
| `=(1+$B$2)^($B$4-A7)` | `power(1 + loss_trend, rating_year - accident_year)` | `1_indication`, step 1 |
| "Save As … V2" | A saved version: the data, the assumptions, the results and a copy of the notebook, under one number | `1_indication`, last cell |
| Opening last month's workbook | Open the copy in `saved_versions` and click Run all | `3_compare_and_reproduce` |
| "Save as v5_FINAL" for picks | A new `version` in the selection table. Earlier versions stay | `3_development_factors`, `4_trend` |
| A named formula (`LAMBDA`) | A Unity Catalog function (optional, later) | `make_it_a_function` |

## Loss trend workbook: tab to notebook to table

| Tab in the workbook | What it is | Notebook | Table |
|---|---|---|---|
| Notes | Valuation date and method notes | `2_triangles` (the valuation date, first line of the query) | |
| Claims | Pasted data | `1_load_the_workbook` | `lt_claims` |
| Loss Data | Pasted data | `1_load_the_workbook` | `lt_loss_data` |
| Premium Data | Pasted data | `1_load_the_workbook` | `lt_premium_data` |
| Triangle | Incurred triangle | `2_triangles` | `lt_triangle` (column `incurred`) |
| Freq & Severity Triangles, block A | Reported claims triangle | `2_triangles` | `lt_triangle` (column `reported_claims`) |
| Triangle row 34; Freq & Severity Triangles row 19 | Volume-weighted age-to-age factors | `3_development_factors` | `lt_ldf_empirical` |
| LDF Selections, column G | Selected factors (yellow cells) | `3_development_factors` | `lt_ldf_selection` |
| LDF Selections, column J | Cumulative factors to ultimate | `3_development_factors` | `lt_cdf` |
| Frequency Trend and Severity Trend, rows 5 to 16 | Ultimate claims, frequency and severity | `4_trend` | `lt_ultimates` |
| Frequency Trend and Severity Trend, rows 21 to 24 | Trend fits | `4_trend` | `lt_trend_fits` |
| Frequency Trend and Severity Trend, rows 28 to 31 | Selected trends (yellow cells) | `4_trend` | `lt_trend_selection` |

## Left out on purpose

To keep the example short, the notebooks leave out some parts of the workbook. All can be added the same way.

- The paid triangle and the non-zero claim count triangle.
- A tail factor, and picks at ages where the data has no factor yet (132 to 144 months). Both count as 1.000, as in the workbook.
- The simple-average factors and the "Prior (last review)" column. Here, the prior is the previous version in `lt_ldf_selection`.
- The rolling trend columns (a fit ending at each accident year) and R².
- The AY Summary and Premium & Exposure tabs.
