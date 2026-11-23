# Databricks notebook source
# MAGIC %md
# MAGIC # Loss trend · 3 of 5 · Development factors
# MAGIC
# MAGIC **In the workbook:** the "Vol-weighted" row under each triangle, then the **LDF Selections** tab, where the yellow cells are the actuary's picks. (LDF = loss development factor, here the age-to-age factor.)
# MAGIC
# MAGIC **Here:** three steps.
# MAGIC 1. Calculate the factors from the triangle.
# MAGIC 2. Record your picks in a table, `lt_ldf_selection`. Every run adds a new version; earlier versions stay.
# MAGIC 3. Multiply the selected factors to get the cumulative factors to ultimate.
# MAGIC
# MAGIC Run `2_triangles` first.

# COMMAND ----------

# Where to work. To change it, use the two boxes at the top of the page, not this code.
dbutils.widgets.text("catalog", spark.catalog.currentCatalog())
dbutils.widgets.text("schema", "excel_to_notebook")
spark.sql(f"USE CATALOG `{dbutils.widgets.get('catalog')}`")
spark.sql(f"USE SCHEMA `{dbutils.widgets.get('schema')}`")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 · Factors from the data
# MAGIC Volume-weighted age-to-age factor = total at the next age ÷ total at this age, over the accident years where the next age is complete.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE lt_ldf_empirical AS
# MAGIC SELECT this_age.age AS age_from,
# MAGIC        next_age.age AS age_to,
# MAGIC        sum(next_age.reported_claims) / sum(this_age.reported_claims) AS claims_factor,     -- Freq & Severity Triangles, row 19
# MAGIC        sum(next_age.incurred) / sum(this_age.incurred)               AS incurred_factor    -- Triangle, row 34
# MAGIC FROM lt_triangle AS this_age
# MAGIC JOIN lt_triangle AS next_age
# MAGIC   ON next_age.accident_year = this_age.accident_year AND next_age.age = this_age.age + 12
# MAGIC WHERE next_age.complete
# MAGIC GROUP BY this_age.age, next_age.age;
# MAGIC
# MAGIC SELECT * FROM lt_ldf_empirical ORDER BY age_from;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 · Record your picks
# MAGIC First, the table that keeps every selection. This runs once; after that it does nothing.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS lt_ldf_selection (
# MAGIC   version INT, age_from INT, age_to INT,
# MAGIC   claims_empirical DOUBLE, claims_selected DOUBLE,
# MAGIC   incurred_empirical DOUBLE, incurred_selected DOUBLE,
# MAGIC   reason STRING, selected_by STRING, selected_at TIMESTAMP);
# MAGIC
# MAGIC CREATE OR REPLACE VIEW lt_ldf_latest AS
# MAGIC SELECT * FROM lt_ldf_selection WHERE version = (SELECT max(version) FROM lt_ldf_selection);

# COMMAND ----------

# MAGIC %md
# MAGIC Review before you pick: the factors from the data next to the last selection. The "last" columns are empty on the first run.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT data.age_from, data.age_to,
# MAGIC        round(data.claims_factor, 3)     AS claims_from_data,
# MAGIC        round(last.claims_selected, 3)   AS claims_last_selected,
# MAGIC        round(data.incurred_factor, 3)   AS incurred_from_data,
# MAGIC        round(last.incurred_selected, 3) AS incurred_last_selected
# MAGIC FROM lt_ldf_empirical AS data
# MAGIC LEFT JOIN lt_ldf_latest AS last USING (age_from)
# MAGIC ORDER BY age_from

# COMMAND ----------

# MAGIC %md
# MAGIC **Your picks: this is the cell you edit.** It is the yellow cells. List only the ages where you choose a different factor from the data, with your reason. `NULL` means "keep the factor from the data". For no picks at all, use `(12, NULL, NULL, NULL)`.
# MAGIC
# MAGIC The workbook has one pick: reported claims 12 to 24 months at **1.650** (the data says 1.717).

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMP VIEW my_picks AS
# MAGIC SELECT * FROM VALUES
# MAGIC   --  age_from, claims factor, incurred factor, reason
# MAGIC   (12, 1.650, NULL, 'Reporting delays in 2021-22 inflate the recent 12-24 factors. Selected below the data.')
# MAGIC   -- , (24, NULL, 1.250, 'Another pick would go here')
# MAGIC AS picks (age_from, claims_factor, incurred_factor, reason);

# COMMAND ----------

# MAGIC %md
# MAGIC **Save as a new version.** Nothing to edit here. Each run adds a version; earlier versions stay.

# COMMAND ----------

# MAGIC %sql
# MAGIC INSERT INTO lt_ldf_selection
# MAGIC SELECT (SELECT coalesce(max(version), 0) + 1 FROM lt_ldf_selection) AS version,
# MAGIC        age_from, age_to,
# MAGIC        data.claims_factor                                       AS claims_empirical,
# MAGIC        coalesce(my_picks.claims_factor, data.claims_factor)     AS claims_selected,
# MAGIC        data.incurred_factor                                     AS incurred_empirical,
# MAGIC        coalesce(my_picks.incurred_factor, data.incurred_factor) AS incurred_selected,
# MAGIC        my_picks.reason,
# MAGIC        current_user()      AS selected_by,
# MAGIC        current_timestamp() AS selected_at
# MAGIC FROM lt_ldf_empirical AS data
# MAGIC LEFT JOIN my_picks USING (age_from);
# MAGIC
# MAGIC SELECT * FROM lt_ldf_latest ORDER BY age_from;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 · Cumulative factors to ultimate
# MAGIC In Excel: `=PRODUCT(...)` of the selected factors from that age onward (**LDF Selections**, column J). This is the CDF, the cumulative development factor.
# MAGIC SQL has no PRODUCT, so we add the logs and take the exponent, which is the same thing. Where there is no factor yet (132 to 144), the result is 1.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE lt_cdf AS
# MAGIC SELECT ages.age,
# MAGIC        coalesce(exp(sum(ln(claims_selected))), 1)   AS claims_cdf,
# MAGIC        coalesce(exp(sum(ln(incurred_selected))), 1) AS incurred_cdf
# MAGIC FROM (SELECT explode(sequence(12, 144, 12)) AS age) AS ages
# MAGIC LEFT JOIN lt_ldf_latest ON lt_ldf_latest.age_from >= ages.age
# MAGIC GROUP BY ages.age;
# MAGIC
# MAGIC SELECT * FROM lt_cdf ORDER BY age;

# COMMAND ----------

# MAGIC %md
# MAGIC Compare with `LDF Selections!J6`: the claims factor at 12 months is 2.140.
# MAGIC
# MAGIC **Next:** `4_trend`
# MAGIC
# MAGIC *About this example: the data is synthetic and the code is a sample to learn from.*
