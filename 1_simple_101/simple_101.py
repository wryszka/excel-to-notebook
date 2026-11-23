# Databricks notebook source
# MAGIC %md
# MAGIC # Simple 101: one small spreadsheet, moved to Databricks
# MAGIC
# MAGIC The workbook `simple_101.xlsx` sits next to this notebook. Open it in Excel first. It has three tabs:
# MAGIC
# MAGIC | Tab | What it holds |
# MAGIC |---|---|
# MAGIC | **Claims** | 60 claims: accident year, paid, outstanding. Column E is a formula: incurred = paid + outstanding |
# MAGIC | **Premium** | Earned premium for each accident year |
# MAGIC | **Summary** | Formulas: claim count, incurred, premium, loss ratio and average claim for each year |
# MAGIC
# MAGIC This notebook does the same in four steps: read the tabs, save them as tables, calculate the Summary tab, check the numbers.
# MAGIC
# MAGIC **To run it:** click **Run all**. The tables go to your workspace's default catalog, in a schema called `excel_to_notebook`. To use another catalog, type its name in the **catalog** box that appears at the top, and run again.

# COMMAND ----------

# MAGIC %pip install openpyxl --quiet

# COMMAND ----------

# Where to work. To change it, use the two boxes at the top of the page, not this code.
dbutils.widgets.text("catalog", spark.catalog.currentCatalog())
dbutils.widgets.text("schema", "excel_to_notebook")
spark.sql(f"USE CATALOG `{dbutils.widgets.get('catalog')}`")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{dbutils.widgets.get('schema')}`")
spark.sql(f"USE SCHEMA `{dbutils.widgets.get('schema')}`")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 · Read the tabs
# MAGIC We read the data you typed or pasted (columns A to D of Claims, and Premium). We don't read the formulas: we redo them below.

# COMMAND ----------

import pandas as pd

workbook = "simple_101.xlsx"
claims = pd.read_excel(workbook, sheet_name="Claims", usecols="A:D")
premium = pd.read_excel(workbook, sheet_name="Premium")

display(claims)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 · Save them as tables
# MAGIC A table is a tab that everyone can find and query. Tables live in a schema (think: folder), and schemas live in a catalog (think: drive). Column names become lower case with underscores (`Accident Year` → `accident_year`).

# COMMAND ----------

def save_as_table(data, table):
    data.columns = [name.lower().replace(" ", "_") for name in data.columns]
    spark.createDataFrame(data).write.mode("overwrite").saveAsTable(table)

save_as_table(claims, "simple_claims")
save_as_table(premium, "simple_premium")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 · The Summary tab, as one query
# MAGIC Each line has the Excel formula it replaces on the right.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE simple_summary AS
# MAGIC SELECT accident_year,
# MAGIC        count(*)                      AS claims,           -- =COUNTIFS(Claims!B:B, A2)
# MAGIC        sum(paid + outstanding)       AS incurred,         -- =SUMIFS(Claims!E:E, Claims!B:B, A2)   where E = C + D
# MAGIC        earned_premium,                                    -- =VLOOKUP(A2, Premium!A:B, 2, FALSE)
# MAGIC        incurred / earned_premium     AS loss_ratio,       -- =C2/D2
# MAGIC        incurred / claims             AS average_claim     -- =C2/B2
# MAGIC FROM simple_claims
# MAGIC JOIN simple_premium USING (accident_year)
# MAGIC GROUP BY accident_year, earned_premium;              -- one row for each year
# MAGIC
# MAGIC SELECT * FROM simple_summary ORDER BY accident_year;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 · Check against the spreadsheet
# MAGIC Now we do read the Summary tab, to compare Excel's answers with ours.

# COMMAND ----------

excel = pd.read_excel(workbook, sheet_name="Summary").head(5).set_index("Accident Year")   # the five year rows, without the Total row
ours = spark.table("simple_summary").toPandas().set_index("accident_year").sort_index()

difference = abs(excel.to_numpy() - ours.to_numpy()).max()
print(f"{excel.size} numbers compared with the Summary tab. Largest difference: {difference:.6f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## What you have now
# MAGIC - Three tables in the schema you chose: `simple_claims`, `simple_premium` and `simple_summary`. Find them under **Catalog** in the left menu.
# MAGIC - A calculation you can read top to bottom, instead of formulas spread over cells.
# MAGIC - Next month: replace the file and click **Run all**.
# MAGIC
# MAGIC **Next:** the same route for a real-size pricing workbook, in the folder `2_loss_trend`.
# MAGIC
# MAGIC *About this example: the data is synthetic and the code is a sample to learn from.*
