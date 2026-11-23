# Databricks notebook source
# MAGIC %md
# MAGIC # Loss trend · 5 of 5 · Check against the workbook
# MAGIC
# MAGIC Notebooks 2 to 4 rebuilt the calculation tabs from the pasted data. This notebook reads Excel's own answers from those tabs and compares them with our tables, number by number.
# MAGIC
# MAGIC You don't need to read the code here. Click **Run all** and look at the result at the bottom.
# MAGIC
# MAGIC Run `4_trend` first.

# COMMAND ----------

# MAGIC %pip install openpyxl --quiet

# COMMAND ----------

# Where to work. To change it, use the two boxes at the top of the page, not this code.
dbutils.widgets.text("catalog", spark.catalog.currentCatalog())
dbutils.widgets.text("schema", "excel_to_notebook")
spark.sql(f"USE CATALOG `{dbutils.widgets.get('catalog')}`")
spark.sql(f"USE SCHEMA `{dbutils.widgets.get('schema')}`")

# COMMAND ----------

from openpyxl import load_workbook

workbook = load_workbook("LossTrend_PL_US_AY2015plus_v4_FINAL.xlsx", data_only=True)   # data_only = Excel's calculated values

def excel(tab, cells):
    """The numbers in a block of cells, row by row. Blank cells are left out."""
    return [cell.value for row in workbook[tab][cells] for cell in row if isinstance(cell.value, (int, float))]

def ours(query):
    """The numbers a query returns, row by row."""
    return [float(value) for row in spark.sql(query).collect() for value in row]

checks = [
    ("Incurred triangle",          excel("Triangle", "B6:M17"),                  ours("SELECT incurred FROM lt_triangle ORDER BY accident_year, age")),
    ("Reported claims triangle",   excel("Freq & Severity Triangles", "C7:N18"), ours("SELECT reported_claims FROM lt_triangle ORDER BY accident_year, age")),
    ("Incurred factors from data", excel("Triangle", "B34:L34"),                 ours("SELECT incurred_factor FROM lt_ldf_empirical ORDER BY age_from")),
    ("Claims factors from data",   excel("Freq & Severity Triangles", "C19:M19"), ours("SELECT claims_factor FROM lt_ldf_empirical ORDER BY age_from")),
    ("Claims factors to ultimate", excel("LDF Selections", "J6:J17"),            ours("SELECT claims_cdf FROM lt_cdf ORDER BY age")),
    ("Incurred factors to ultimate", excel("LDF Selections", "J22:J33"),         ours("SELECT incurred_cdf FROM lt_cdf ORDER BY age")),
    ("Ultimate frequency",         excel("Frequency Trend", "G5:G16"),           ours("SELECT frequency FROM lt_ultimates ORDER BY accident_year")),
    ("Ultimate severity",          excel("Severity Trend", "G5:G16"),            ours("SELECT severity FROM lt_ultimates ORDER BY accident_year")),
    ("Frequency trend fits",       excel("Frequency Trend", "E21:E24"),          ours("SELECT frequency_trend FROM lt_trend_fits ORDER BY start_year DESC")),
    ("Severity trend fits",        excel("Severity Trend", "E21:E24"),           ours("SELECT severity_trend FROM lt_trend_fits ORDER BY start_year DESC")),
]

total = 0
total_different = 0
for name, from_excel, from_tables in checks:
    assert len(from_excel) == len(from_tables), f"{name}: Excel has {len(from_excel)} numbers, the table has {len(from_tables)}"
    # "Different" = not equal to 9 significant figures
    different = sum(1 for a, b in zip(from_excel, from_tables) if abs(a - b) > 1e-9 * max(abs(a), 1))
    print(f"{name:<30} {len(from_excel):>4} numbers compared, {different} different")
    total += len(from_excel)
    total_different += different

print(f"\nAll together: {total} numbers compared with the workbook, {total_different} different.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## What you have now
# MAGIC - The workbook's pasted data as three tables, and each calculation tab as a short query you can read.
# MAGIC - The same numbers as Excel.
# MAGIC - The factor and trend picks stored as versions: who, when, why.
# MAGIC
# MAGIC To try a change: go back to `3_development_factors`, change a pick, and run notebooks 3 and 4 again. A new version is recorded. This check will then show differences, because the workbook still holds the old pick.
# MAGIC
# MAGIC **Next:** make a calculation reusable, in the folder `3_unity_catalog_function`.
# MAGIC
# MAGIC *About this example: the data is synthetic and the code is a sample to learn from.*
