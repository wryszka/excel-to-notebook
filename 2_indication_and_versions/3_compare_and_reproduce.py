# Databricks notebook source
# MAGIC %md
# MAGIC # Your calculation, your versions · 3 of 3 · Compare and reproduce
# MAGIC
# MAGIC You saved some versions in `1_indication`. This notebook answers the questions you'd ask of a folder of workbooks named V1, V2, V3:
# MAGIC
# MAGIC 1. What did I calculate, and when?
# MAGIC 2. What changed between two versions: the assumptions, the data, the formulas?
# MAGIC 3. Which version produced the published figures?
# MAGIC 4. Can I reproduce an old result?
# MAGIC
# MAGIC Save at least two versions first.

# COMMAND ----------

# Where to work. To change it, use the two boxes at the top of the page, not this code.
dbutils.widgets.text("catalog", spark.catalog.currentCatalog())
dbutils.widgets.text("schema", "excel_to_notebook")
spark.sql(f"USE CATALOG `{dbutils.widgets.get('catalog')}`")
spark.sql(f"USE SCHEMA `{dbutils.widgets.get('schema')}`")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1 · What did I calculate, and when?
# MAGIC One row for each saved version: who, when, what changed, the assumptions and the result.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT version, name, what_changed, saved_by, saved_at,
# MAGIC        loss_trend, target_loss_ratio, rating_year,
# MAGIC        round(indicated_rate_change * 100, 1) AS indicated_rate_change_pct,
# MAGIC        published
# MAGIC FROM indication_versions
# MAGIC ORDER BY version

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2 · What changed between two versions?
# MAGIC The cells below compare version **1** with version **2**. To compare other versions, change the two numbers in each cell.
# MAGIC
# MAGIC **The results by year.** Look at which years are there (a change of method), the incurred (a change in the data) and the trended losses (a change of assumption).

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT accident_year,
# MAGIC        old.incurred AS incurred_old,             new.incurred AS incurred_new,
# MAGIC        round(old.trended_losses) AS trended_old, round(new.trended_losses) AS trended_new
# MAGIC FROM      (SELECT * FROM indication_saved_by_year WHERE version = 1) AS old
# MAGIC FULL JOIN (SELECT * FROM indication_saved_by_year WHERE version = 2) AS new USING (accident_year)
# MAGIC ORDER BY accident_year

# COMMAND ----------

# MAGIC %md
# MAGIC **The formulas.** Every line of the calculation that differs between the two versions: `-` is the old line, `+` is the new one.

# COMMAND ----------

import difflib

old_version, new_version = 1, 2

code = {row.version: row.calculation_code.splitlines()
        for row in spark.sql(f"SELECT version, calculation_code FROM indication_versions WHERE version IN ({old_version}, {new_version})").collect()}

changes = [line for line in difflib.unified_diff(code[old_version], code[new_version], lineterm="", n=0)
           if line[:1] in "+-" and line[:3] not in ("+++", "---") and "saved" not in line]   # leave out the lines that only carry the version number
print("\n".join(line.replace("# MAGIC ", "", 1) for line in changes) or "No difference in the formulas or assumptions.")

# COMMAND ----------

# MAGIC %md
# MAGIC To read the whole calculation of an old version, open its copy in the folder `saved_versions` (next to `1_indication`). The same text is also kept in the list of versions, so it survives even if that copy is deleted:

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT version, name, saved_notebook, calculation_code FROM indication_versions WHERE version = 1

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3 · Which version produced the published figures?
# MAGIC When a version is the one that goes out, mark it. Change the number to the version you publish.

# COMMAND ----------

# MAGIC %sql
# MAGIC UPDATE indication_versions SET published = (version = 2);
# MAGIC
# MAGIC SELECT version, name, saved_by, saved_at, round(indicated_rate_change * 100, 1) AS indicated_rate_change_pct
# MAGIC FROM indication_versions
# MAGIC WHERE published;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4 · Can I reproduce an old result?
# MAGIC Yes. Each saved version has its own copy of the notebook, and that copy reads the data as it was saved, not today's data.
# MAGIC
# MAGIC 1. In the left menu, open the folder `saved_versions`, next to `1_indication`.
# MAGIC 2. Open the copy you want, for example `v1_October_indications`.
# MAGIC 3. Click **Run all**.
# MAGIC 4. Look at the last result. It shows this run next to the saved result, and says `Reproduced: the same result.`
# MAGIC
# MAGIC The data and the working notebook may have changed many times since. The saved version still gives the number it gave on the day.
# MAGIC
# MAGIC **To bring an old formula back:** open the saved copy, copy the cell you want, and paste it into `1_indication`.
# MAGIC
# MAGIC **Next:** the same route for a real-size pricing workbook, in the folder `3_loss_trend`.
# MAGIC
# MAGIC *About this example: the data is synthetic and the code is a sample to learn from.*
