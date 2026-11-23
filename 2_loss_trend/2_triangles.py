# Databricks notebook source
# MAGIC %md
# MAGIC # Loss trend · 2 of 5 · Triangles
# MAGIC
# MAGIC **In the workbook:** the **Triangle** tab (incurred) and the **Freq & Severity Triangles** tab (reported claims).
# MAGIC Each cell is a `SUMIFS` or `COUNTIFS` over the pasted data: accident year in the row, months of development in the column.
# MAGIC
# MAGIC **Here:** one query builds both triangles as a table, `lt_triangle`, with one row for each cell.
# MAGIC
# MAGIC Run `1_load_the_workbook` first.

# COMMAND ----------

# Where to work. To change it, use the two boxes at the top of the page, not this code.
dbutils.widgets.text("catalog", spark.catalog.currentCatalog())
dbutils.widgets.text("schema", "excel_to_notebook")
spark.sql(f"USE CATALOG `{dbutils.widgets.get('catalog')}`")
spark.sql(f"USE SCHEMA `{dbutils.widgets.get('schema')}`")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Build the triangles
# MAGIC The valuation date is 30 September 2026, so the last cell in every row covers part of a year. We mark it `complete = false` and keep it out of the development factors later, as the workbook does.

# COMMAND ----------

# MAGIC %sql
# MAGIC DECLARE OR REPLACE VARIABLE valuation_date DATE DEFAULT DATE'2026-09-30';     -- a named value, like a named cell. Notes tab, cell B4
# MAGIC
# MAGIC CREATE OR REPLACE TABLE lt_triangle AS
# MAGIC WITH cells AS (            -- the empty grid: every accident year (rows) x every age 12, 24 ... 144 (column headings)
# MAGIC   SELECT accident_year, age,
# MAGIC          (year(valuation_date) - accident_year) * 12 + month(valuation_date) AS months_old
# MAGIC   FROM (SELECT DISTINCT accident_year FROM lt_claims)
# MAGIC   CROSS JOIN (SELECT explode(sequence(12, 144, 12)) AS age)        -- the numbers 12, 24 ... 144, one per row
# MAGIC ),
# MAGIC claims AS (               -- =COUNTIFS(accident year = row, report age <= column)
# MAGIC   SELECT cells.accident_year, cells.age, count(*) AS reported_claims
# MAGIC   FROM cells
# MAGIC   JOIN lt_claims ON lt_claims.accident_year = cells.accident_year AND lt_claims.report_age_months <= cells.age
# MAGIC   GROUP BY cells.accident_year, cells.age
# MAGIC ),
# MAGIC losses AS (               -- =SUMIFS(incurred, accident year = row, development age <= column)
# MAGIC   SELECT cells.accident_year, cells.age, sum(lt_loss_data.incurred) AS incurred
# MAGIC   FROM cells
# MAGIC   JOIN lt_loss_data ON lt_loss_data.accident_year = cells.accident_year AND lt_loss_data.dev_age_months <= cells.age
# MAGIC   GROUP BY cells.accident_year, cells.age
# MAGIC )
# MAGIC SELECT accident_year, age,
# MAGIC        age <= months_old            AS complete,     -- false = the part-year cell at the end of each row
# MAGIC        coalesce(reported_claims, 0) AS reported_claims,
# MAGIC        coalesce(incurred, 0)        AS incurred
# MAGIC FROM cells
# MAGIC LEFT JOIN claims USING (accident_year, age)
# MAGIC LEFT JOIN losses USING (accident_year, age)
# MAGIC WHERE age - 12 < months_old;                          -- leave out cells in the future

# COMMAND ----------

# MAGIC %md
# MAGIC ## Incurred triangle
# MAGIC Laid out like the **Triangle** tab. Compare the first cell with `Triangle!B6`: 6,274,065.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM (SELECT accident_year, age, incurred FROM lt_triangle)
# MAGIC PIVOT (sum(incurred) FOR age IN (12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144))
# MAGIC ORDER BY accident_year

# COMMAND ----------

# MAGIC %md
# MAGIC ## Reported claims triangle
# MAGIC Laid out like block A of the **Freq & Severity Triangles** tab. Compare the first cell with `C7`: 112.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM (SELECT accident_year, age, reported_claims FROM lt_triangle)
# MAGIC PIVOT (sum(reported_claims) FOR age IN (12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144))
# MAGIC ORDER BY accident_year

# COMMAND ----------

# MAGIC %md
# MAGIC **Next:** `3_development_factors`
# MAGIC
# MAGIC *About this example: the data is synthetic and the code is a sample to learn from.*
