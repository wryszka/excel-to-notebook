# Databricks notebook source
# MAGIC %md
# MAGIC # Later, when you need it: make a calculation reusable
# MAGIC
# MAGIC *This part is optional. Nothing before it depends on it.*
# MAGIC
# MAGIC So far each formula lives in a notebook cell. That's the right place to start.
# MAGIC
# MAGIC When several people or several notebooks need the same formula, give it a name. A **function** is a named formula that is stored in the catalog, next to the tables. Everyone who is allowed to can call it, from a notebook, a query or a dashboard, and they all get the same calculation.
# MAGIC
# MAGIC It's the same idea as a named formula in Excel (`LAMBDA`), but shared and with permissions.
# MAGIC
# MAGIC This notebook makes two. Run the `1_simple_101` and `3_loss_trend` notebooks first.

# COMMAND ----------

# Where to work. To change it, use the two boxes at the top of the page, not this code.
dbutils.widgets.text("catalog", spark.catalog.currentCatalog())
dbutils.widgets.text("schema", "excel_to_notebook")
spark.sql(f"USE CATALOG `{dbutils.widgets.get('catalog')}`")
spark.sql(f"USE SCHEMA `{dbutils.widgets.get('schema')}`")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1 · A function that returns one number
# MAGIC The loss ratio from the simple 101 notebook. There are three parts: the inputs, the type of the result, and the formula after `RETURN`.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE FUNCTION loss_ratio(incurred DOUBLE, earned_premium DOUBLE)
# MAGIC RETURNS DOUBLE
# MAGIC COMMENT 'Incurred loss divided by earned premium'
# MAGIC RETURN incurred / earned_premium;

# COMMAND ----------

# MAGIC %md
# MAGIC Use it like any built-in function.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT accident_year, incurred, earned_premium,
# MAGIC        loss_ratio(incurred, earned_premium) AS loss_ratio
# MAGIC FROM simple_summary
# MAGIC ORDER BY accident_year

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2 · A function that returns a table
# MAGIC The trend fit from notebook `4_trend`, with the number of years as an input. The query after `RETURN` is the one you already ran there.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE FUNCTION trend_fit(years INT)
# MAGIC RETURNS TABLE (start_year INT, end_year INT, frequency_trend DOUBLE, severity_trend DOUBLE)
# MAGIC COMMENT 'Annual frequency and severity trend over the last N mature accident years. Same fit as LOGEST - 1 in Excel'
# MAGIC RETURN
# MAGIC   SELECT min(accident_year), max(accident_year),
# MAGIC          exp(regr_slope(ln(frequency), accident_year)) - 1,
# MAGIC          exp(regr_slope(ln(severity),  accident_year)) - 1
# MAGIC   FROM (SELECT *, max(accident_year) OVER () AS last_year FROM lt_ultimates WHERE mature)
# MAGIC   WHERE accident_year > last_year - trend_fit.years;

# COMMAND ----------

# MAGIC %md
# MAGIC Now any window is one line. The workbook has 3, 5 and 8 years; here is 4.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM trend_fit(4)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3 · Where it lives, and who can use it
# MAGIC - Open **Catalog** in the left menu, go to your schema and look under **Functions**. Both functions are there, with their comments and the formula.
# MAGIC - To let a group use one, grant it. Remove the `--`, put in a real group name, and run. (They also need `USE CATALOG` and `USE SCHEMA` on the catalog and schema.)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- GRANT EXECUTE ON FUNCTION trend_fit TO `pricing-team`;
# MAGIC
# MAGIC DESCRIBE FUNCTION trend_fit

# COMMAND ----------

# MAGIC %md
# MAGIC ## When to make a function
# MAGIC - **Keep it in a notebook cell** while you're still working out the calculation, or when only one notebook uses it.
# MAGIC - **Make it a function** when the same formula is needed in more than one place and must give the same answer everywhere.
# MAGIC
# MAGIC These two are written in SQL. A function can also be written in Python, for a formula SQL can't express.
# MAGIC
# MAGIC *About this example: the data is synthetic and the code is a sample to learn from.*
