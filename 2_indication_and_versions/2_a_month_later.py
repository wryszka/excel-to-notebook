# Databricks notebook source
# MAGIC %md
# MAGIC # Your calculation, your versions · 2 of 3 · A month later
# MAGIC
# MAGIC A month passes and the data moves: one more claim of 60,000 is reported for accident year 2025.
# MAGIC
# MAGIC This notebook makes that change to the data, so you can see what a saved version protects you from. Run it **once**.
# MAGIC
# MAGIC To put the data back as it was, run `1_simple_101/simple_101` again.

# COMMAND ----------

# Where to work. To change it, use the two boxes at the top of the page, not this code.
dbutils.widgets.text("catalog", spark.catalog.currentCatalog())
dbutils.widgets.text("schema", "excel_to_notebook")
spark.sql(f"USE CATALOG `{dbutils.widgets.get('catalog')}`")
spark.sql(f"USE SCHEMA `{dbutils.widgets.get('schema')}`")

# COMMAND ----------

# MAGIC %sql
# MAGIC UPDATE simple_summary
# MAGIC SET claims        = claims + 1,
# MAGIC     incurred      = incurred + 60000,
# MAGIC     loss_ratio    = (incurred + 60000) / earned_premium,
# MAGIC     average_claim = (incurred + 60000) / (claims + 1)
# MAGIC WHERE accident_year = 2025;
# MAGIC
# MAGIC SELECT * FROM simple_summary ORDER BY accident_year;

# COMMAND ----------

# MAGIC %md
# MAGIC Accident year 2025 now shows 11 claims and incurred of 212,600.
# MAGIC
# MAGIC **Now:** go back to `1_indication` and click **Run all**. The result has moved, because the data has. Save it under a new name, for example `December indications`.
# MAGIC
# MAGIC The versions you saved before still hold the data as it was when you saved them. See that in `3_compare_and_reproduce`.
# MAGIC
# MAGIC *About this example: the data is synthetic and the code is a sample to learn from.*
