# Databricks notebook source
# MAGIC %md
# MAGIC # Your calculation, your versions · 1 of 3 · The indication
# MAGIC
# MAGIC **In the workbook:** the **Indication** tab of `simple_101.xlsx` (in the folder `1_simple_101`). It has three assumptions in yellow cells and a small rate indication.
# MAGIC
# MAGIC **Here:** the same calculation, top to bottom: the data, the assumptions, two calculation steps, the result. At the end you can save it as a version, as you would save a workbook as "V1".
# MAGIC
# MAGIC The mathematics is deliberately simple and for illustration only: no development to ultimate, no on-levelling, no expenses.
# MAGIC
# MAGIC Everything here is yours to change: the assumptions and the formulas. Change a cell, click **Run all**, and see the new result.
# MAGIC
# MAGIC Run `1_simple_101/simple_101` first: this notebook uses its summary table.

# COMMAND ----------

# Where to work, and the two boxes for saving a version. Use the boxes at the top of the page, not this code.
dbutils.widgets.text("catalog", spark.catalog.currentCatalog())
dbutils.widgets.text("schema", "excel_to_notebook")
dbutils.widgets.text("save_as", "")
dbutils.widgets.text("what_changed", "")
spark.sql(f"USE CATALOG `{dbutils.widgets.get('catalog')}`")
spark.sql(f"USE SCHEMA `{dbutils.widgets.get('schema')}`")

# COMMAND ----------

# MAGIC %md
# MAGIC ## The data
# MAGIC Earned premium and incurred losses by accident year: the table you built in the simple 101.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMP VIEW input_data AS
# MAGIC SELECT accident_year, earned_premium, incurred
# MAGIC FROM simple_summary;
# MAGIC
# MAGIC SELECT * FROM input_data ORDER BY accident_year;

# COMMAND ----------

# MAGIC %md
# MAGIC ## The assumptions
# MAGIC These are the yellow cells (`Indication!B2:B4`). **Change them here.**

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMP VIEW assumptions AS
# MAGIC SELECT 0.05 AS loss_trend,           -- annual loss trend
# MAGIC        0.48 AS target_loss_ratio,    -- the loss ratio the rates should achieve
# MAGIC        2027 AS rating_year;          -- the year the new rates apply to
# MAGIC
# MAGIC SELECT * FROM assumptions;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 · Trend the losses to the rating year
# MAGIC Each line has the Excel formula it replaces on the right (row 7 of the Indication tab).

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMP VIEW by_year AS
# MAGIC SELECT accident_year,
# MAGIC        earned_premium,
# MAGIC        incurred,
# MAGIC        incurred / earned_premium                           AS loss_ratio,        -- =C7/B7
# MAGIC        power(1 + loss_trend, rating_year - accident_year)  AS trend_factor,      -- =(1+$B$2)^($B$4-A7)
# MAGIC        incurred * trend_factor                             AS trended_losses     -- =C7*E7
# MAGIC FROM input_data
# MAGIC CROSS JOIN assumptions                                                           -- makes the assumptions available on every row
# MAGIC -- WHERE accident_year >= 2023      -- a change of method: to use the last three years only, remove the two dashes at the start of this line
# MAGIC ;
# MAGIC
# MAGIC SELECT * FROM by_year ORDER BY accident_year;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 · The indicated rate change
# MAGIC Trended loss ratio = trended losses ÷ earned premium, over all the years above. Indicated rate change = trended loss ratio ÷ target loss ratio − 1.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TEMP VIEW result AS
# MAGIC SELECT sum(trended_losses) / sum(earned_premium)                               AS trended_loss_ratio,      -- =F12/B12
# MAGIC        sum(trended_losses) / sum(earned_premium) / max(target_loss_ratio) - 1  AS indicated_rate_change    -- =B14/B3-1
# MAGIC FROM by_year
# MAGIC CROSS JOIN assumptions;
# MAGIC
# MAGIC SELECT round(trended_loss_ratio * 100, 1)    AS trended_loss_ratio_pct,
# MAGIC        round(indicated_rate_change * 100, 1) AS indicated_rate_change_pct
# MAGIC FROM result;

# COMMAND ----------

# MAGIC %md
# MAGIC With the assumptions as delivered, the result is **+3.8%**, the same as `Indication!B15` in the workbook.
# MAGIC
# MAGIC ## Try it: change the calculation
# MAGIC 1. **Change an assumption.** In **The assumptions**, change `0.05` to `0.06`. Click **Run all**. The result becomes +7.8%.
# MAGIC 2. **Change the method.** In **Step 1**, remove the two dashes in front of `WHERE accident_year >= 2023`. Click **Run all**. The result becomes +5.0%.
# MAGIC
# MAGIC Nothing was saved by doing this. You're working on a draft, as in an open workbook.
# MAGIC
# MAGIC ## Save this version
# MAGIC When you're happy with a calculation, save it, as you would "Save As … V2".
# MAGIC 1. In the **save_as** box at the top, type a name, for example `October indications`.
# MAGIC 2. In **what_changed**, type a short description.
# MAGIC 3. Click **Run all**.
# MAGIC
# MAGIC Saving keeps four things together under one version number: the data as it is now, the assumptions, the results, and a copy of this notebook with its formulas. A saved version is never overwritten.
# MAGIC
# MAGIC The next cell creates the three tables where versions are kept (it runs once). The last cell does the saving. You don't need to read its code.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS indication_versions (
# MAGIC   version INT, name STRING, what_changed STRING, saved_by STRING, saved_at TIMESTAMP,
# MAGIC   loss_trend DOUBLE, target_loss_ratio DOUBLE, rating_year INT,
# MAGIC   trended_loss_ratio DOUBLE, indicated_rate_change DOUBLE,
# MAGIC   published BOOLEAN, saved_notebook STRING, calculation_code STRING);
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS indication_saved_inputs (
# MAGIC   version INT, accident_year BIGINT, earned_premium DOUBLE, incurred DOUBLE);
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS indication_saved_by_year (
# MAGIC   version INT, accident_year BIGINT, earned_premium DOUBLE, incurred DOUBLE,
# MAGIC   loss_ratio DOUBLE, trend_factor DOUBLE, trended_losses DOUBLE);

# COMMAND ----------

import base64, re
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import ExportFormat, ImportFormat, Language

save_as = dbutils.widgets.get("save_as").strip()
what_changed = dbutils.widgets.get("what_changed").strip()
saved_copy_of = 0      # 0 = the working notebook. In a saved copy, this is its version number.

this_run = spark.table("result").first()
print(f"This run: indicated rate change {this_run.indicated_rate_change:+.1%}")

if saved_copy_of:
    # This is a saved copy: it reads the saved data. Compare this run with the result that was saved.
    saved = spark.sql(f"SELECT name, indicated_rate_change FROM indication_versions WHERE version = {saved_copy_of}").first()
    same = abs(saved.indicated_rate_change - this_run.indicated_rate_change) < 1e-12
    print(f"Saved as version {saved_copy_of} ({saved.name}): {saved.indicated_rate_change:+.1%}")
    print("Reproduced: the same result." if same else "Different from the saved result: this copy has been edited.")

elif not save_as:
    print("Draft: nothing was saved. To save this as a version, type a name in the save_as box at the top and click Run all.")

elif spark.sql("SELECT 1 FROM indication_versions WHERE name = :name", args={"name": save_as}).count():
    print(f"'{save_as}' is already saved, and saved versions are never overwritten. To save this run, type a new name in save_as.")

else:
    version = spark.sql("SELECT coalesce(max(version), 0) + 1 FROM indication_versions").first()[0]

    # 1. The data as it is now, and the results by year
    spark.sql(f"INSERT INTO indication_saved_inputs SELECT {version}, accident_year, earned_premium, incurred FROM input_data")
    spark.sql(f"INSERT INTO indication_saved_by_year SELECT {version}, * FROM by_year")

    # 2. A copy of this notebook, set to read the saved data instead of today's data
    workspace = WorkspaceClient().workspace
    this_notebook = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
    code = base64.b64decode(workspace.export(this_notebook, format=ExportFormat.SOURCE).content).decode()
    code = code.replace("FROM simple_summary;", f"FROM indication_saved_inputs WHERE version = {version};", 1)
    code = code.replace("saved_copy_of = 0", f"saved_copy_of = {version}", 1)
    folder = this_notebook.rsplit("/", 1)[0] + "/saved_versions"
    saved_notebook = f"{folder}/v{version}_" + re.sub(r"\W+", "_", save_as)
    workspace.mkdirs(folder)
    workspace.import_(path=saved_notebook, content=base64.b64encode(code.encode()).decode(),
                      format=ImportFormat.SOURCE, language=Language.PYTHON)

    # 3. One row in the list of versions: who, when, what changed, the assumptions, the result, the formulas
    spark.sql("""
        INSERT INTO indication_versions
        SELECT :version, :name, :what_changed, current_user(), current_timestamp(),
               loss_trend, target_loss_ratio, rating_year,
               trended_loss_ratio, indicated_rate_change,
               false, :saved_notebook, :code
        FROM assumptions CROSS JOIN result""",
        args={"version": version, "name": save_as, "what_changed": what_changed, "saved_notebook": saved_notebook, "code": code})

    print(f"Saved as version {version}: {save_as}")
    print(f"A copy of this notebook is in the folder saved_versions, next to this notebook: v{version}_...")

# COMMAND ----------

# MAGIC %md
# MAGIC **Next:** `2_a_month_later` (new data arrives), then `3_compare_and_reproduce`.
# MAGIC
# MAGIC *About this example: the data is synthetic, the calculation is illustrative, and the code is a sample to learn from.*
