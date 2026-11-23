# Databricks notebook source
# MAGIC %md
# MAGIC # Loss trend · 4 of 5 · Ultimate frequency, severity and the trend picks
# MAGIC
# MAGIC **In the workbook:** the **Frequency Trend** and **Severity Trend** tabs. They develop each accident year to ultimate, fit trends with `LOGEST`, and hold the selected trends at the bottom.
# MAGIC
# MAGIC **Here:** three steps.
# MAGIC 1. Develop each accident year to ultimate.
# MAGIC 2. Fit the trends over 3, 5 and 8 years and all years.
# MAGIC 3. Record your trend picks in a table, `lt_trend_selection`.
# MAGIC
# MAGIC Run `3_development_factors` first.

# COMMAND ----------

# Where to work. To change it, use the two boxes at the top of the page, not this code.
dbutils.widgets.text("catalog", spark.catalog.currentCatalog())
dbutils.widgets.text("schema", "excel_to_notebook")
spark.sql(f"USE CATALOG `{dbutils.widgets.get('catalog')}`")
spark.sql(f"USE SCHEMA `{dbutils.widgets.get('schema')}`")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 · Develop each accident year to ultimate
# MAGIC Ultimate = the latest cell in the row × the cumulative factor at that age.
# MAGIC The latest cell covers part of a year (for example 21 months) and takes the factor of its column (24 months), as the workbook does. On your own data, a year-end valuation avoids this shortcut.
# MAGIC Frequency = ultimate claims per 100 exposures. Severity = ultimate incurred per ultimate claim.
# MAGIC The latest accident year is a part year: we show it, but leave it out of the trend fits (`mature = false`).

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE lt_ultimates AS
# MAGIC WITH latest AS (           -- the last cell in each row of the triangle
# MAGIC   SELECT * FROM lt_triangle
# MAGIC   QUALIFY age = max(age) OVER (PARTITION BY accident_year)      -- keep the row with the highest age for each accident year
# MAGIC ),
# MAGIC exposure AS (             -- =SUMIFS('Premium Data'!F:F, 'Premium Data'!A:A, accident year)
# MAGIC   SELECT calendar_year AS accident_year, sum(earned_exposure) AS earned_exposure
# MAGIC   FROM lt_premium_data
# MAGIC   GROUP BY calendar_year
# MAGIC )
# MAGIC SELECT accident_year,
# MAGIC        earned_exposure,
# MAGIC        reported_claims * claims_cdf           AS ultimate_claims,      -- Frequency Trend, column F
# MAGIC        incurred * incurred_cdf                AS ultimate_incurred,    -- Severity Trend, column F
# MAGIC        ultimate_claims / earned_exposure * 100 AS frequency,           -- Frequency Trend, column G
# MAGIC        ultimate_incurred / ultimate_claims    AS severity,             -- Severity Trend, column G
# MAGIC        accident_year < max(accident_year) OVER () AS mature
# MAGIC FROM latest
# MAGIC JOIN lt_cdf USING (age)
# MAGIC JOIN exposure USING (accident_year);
# MAGIC
# MAGIC SELECT * FROM lt_ultimates ORDER BY accident_year;

# COMMAND ----------

# The chart from the workbook: ultimate frequency by accident year
spark.table("lt_ultimates").toPandas().sort_values("accident_year").plot(
    x="accident_year", y="frequency", marker="o", title="Ultimate frequency (claims per 100 exposures)");

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 · Fit the trends
# MAGIC In Excel: `=LOGEST(values, years) - 1`. In SQL: `exp(regr_slope(ln(value), year)) - 1`. It is the same fit, so it gives the same number.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE lt_trend_fits AS
# MAGIC WITH mature_years AS (
# MAGIC   SELECT *, max(accident_year) OVER () AS last_year FROM lt_ultimates WHERE mature
# MAGIC )
# MAGIC SELECT fit_window,
# MAGIC        min(accident_year) AS start_year,
# MAGIC        max(accident_year) AS end_year,
# MAGIC        exp(regr_slope(ln(frequency), accident_year)) - 1 AS frequency_trend,   -- Frequency Trend, E21:E24
# MAGIC        exp(regr_slope(ln(severity),  accident_year)) - 1 AS severity_trend     -- Severity Trend, E21:E24
# MAGIC FROM mature_years
# MAGIC JOIN (VALUES ('3-yr', 3), ('5-yr', 5), ('8-yr', 8), ('All years', 99)) AS windows (fit_window, years)
# MAGIC   ON accident_year > last_year - years
# MAGIC GROUP BY fit_window, years;
# MAGIC
# MAGIC SELECT fit_window, start_year, end_year,
# MAGIC        round(frequency_trend * 100, 1) AS frequency_trend_pct,
# MAGIC        round(severity_trend * 100, 1)  AS severity_trend_pct
# MAGIC FROM lt_trend_fits ORDER BY start_year DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 · Record your trend picks
# MAGIC First, the table that keeps every selection. This runs once; after that it does nothing.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS lt_trend_selection (
# MAGIC   version INT, measure STRING, historic_trend DOUBLE, prospective_trend DOUBLE,
# MAGIC   reason STRING, ldf_version INT, selected_by STRING, selected_at TIMESTAMP);

# COMMAND ----------

# MAGIC %md
# MAGIC **Your picks: this is the cell you edit.** These are the yellow cells at the bottom of the two trend tabs: a historic and a prospective trend for each measure, with your reason.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMP VIEW my_picks AS
# MAGIC SELECT * FROM VALUES
# MAGIC   --  measure, historic trend, prospective trend, reason
# MAGIC   ('frequency', 0.025, 0.020, 'The 5-yr fit is the rebound from the 2020-21 dip, not trend. Pre-2020 run-rate is about +2% to +3%.'),
# MAGIC   ('severity',  0.060, 0.060, 'The 8-yr fit, rounded. The 3-yr fit is distorted by large losses in 2023-24.')
# MAGIC AS picks (measure, historic_trend, prospective_trend, reason);

# COMMAND ----------

# MAGIC %md
# MAGIC **Save as a new version.** Nothing to edit here. Each run adds a version, and notes which version of the development factors it was based on.

# COMMAND ----------

# MAGIC %sql
# MAGIC INSERT INTO lt_trend_selection
# MAGIC SELECT (SELECT coalesce(max(version), 0) + 1 FROM lt_trend_selection) AS version,
# MAGIC        measure, historic_trend, prospective_trend, reason,
# MAGIC        (SELECT max(version) FROM lt_ldf_selection) AS ldf_version,
# MAGIC        current_user()      AS selected_by,
# MAGIC        current_timestamp() AS selected_at
# MAGIC FROM my_picks;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Who picked what, when and why
# MAGIC Every version is kept.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM lt_trend_selection ORDER BY version DESC, measure

# COMMAND ----------

# MAGIC %md
# MAGIC **Next:** `5_check_against_the_workbook`
# MAGIC
# MAGIC *About this example: the data is synthetic and the code is a sample to learn from.*
