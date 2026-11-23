# Databricks notebook source
# MAGIC %md
# MAGIC # Loss trend · 1 of 5 · Load the workbook
# MAGIC
# MAGIC The workbook `LossTrend_PL_US_AY2015plus_v4_FINAL.xlsx` sits next to this notebook. Open it in Excel first.
# MAGIC It is a loss trend study for a professional liability book (synthetic data): triangles, development factors, ultimate frequency and severity, and trend picks.
# MAGIC
# MAGIC Three of its tabs are data that someone pastes in. This notebook saves them as tables. The other notebooks redo the calculation tabs.
# MAGIC (A few columns on the Claims tab are formulas, such as the report age. We read their values.)
# MAGIC
# MAGIC | Tab (pasted data) | Table |
# MAGIC |---|---|
# MAGIC | Claims | `lt_claims` |
# MAGIC | Loss Data | `lt_loss_data` |
# MAGIC | Premium Data | `lt_premium_data` |
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

import re
import pandas as pd

workbook = "LossTrend_PL_US_AY2015plus_v4_FINAL.xlsx"

def save_tab_as_table(tab, table):
    data = pd.read_excel(workbook, sheet_name=tab)
    # Column names become lower case with underscores: "Dev Age (months)" -> dev_age_months
    data.columns = [re.sub(r"\W+", "_", name.lower()).strip("_") for name in data.columns]
    spark.createDataFrame(data).write.mode("overwrite").saveAsTable(table)
    print(f"{tab}: {len(data):,} rows saved as {table}")

save_tab_as_table("Claims", "lt_claims")
save_tab_as_table("Loss Data", "lt_loss_data")
save_tab_as_table("Premium Data", "lt_premium_data")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Look at one
# MAGIC The same rows as the Claims tab.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM lt_claims LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ## Later: your own tables instead of the workbook
# MAGIC
# MAGIC The next notebooks read only these columns:
# MAGIC
# MAGIC | Table | Columns used |
# MAGIC |---|---|
# MAGIC | `lt_claims` | `accident_year`, `report_age_months` |
# MAGIC | `lt_loss_data` | `accident_year`, `dev_age_months`, `incurred` |
# MAGIC | `lt_premium_data` | `calendar_year`, `earned_exposure` |
# MAGIC
# MAGIC So to run them on your own claims and premium tables, you create three views with those column names. The steps and a template are in `docs/STEP_BY_STEP.md`, under **Use your own tables**.
# MAGIC
# MAGIC **Next:** `2_triangles`
# MAGIC
# MAGIC *About this example: the data is synthetic and the code is a sample to learn from.*
