# From Excel to a Databricks notebook

Move a spreadsheet calculation into Databricks, one small step at a time, and get the same numbers.

There are three parts. Each one is short, and you can stop after any of them.

| Part | What you do | Time |
|---|---|---|
| [1 · Simple 101](1_simple_101) | A tiny workbook (claims, premium, a summary with `SUMIFS`) becomes three tables and one query | 5 min |
| [2 · Loss trend](2_loss_trend) | A real-size pricing workbook: triangles, development factors, trend picks. Five short notebooks, one for each step | 20 min |
| [3 · Unity Catalog function](3_unity_catalog_function) | Turn a formula from a notebook into a named function that others can call | 5 min |

Each part comes with its Excel file, so you can see the spreadsheet and the notebook side by side. Every part ends with a check that the notebook's numbers equal Excel's.

## Start here

You need a Databricks workspace with Unity Catalog, and a catalog where you can create a schema.

1. In Databricks, click **Workspace** in the left menu, then **Create → Git folder**.
2. Paste `https://github.com/wryszka/excel-to-notebook` and click **Create Git folder**. No login to GitHub is needed.
3. Open `1_simple_101/simple_101`.
4. Click **Run all**.

The full walkthrough, with what you should see at each step, is in [docs/STEP_BY_STEP.md](docs/STEP_BY_STEP.md). The mapping from Excel formulas to SQL, and from each tab to its notebook and table, is in [docs/EXCEL_TO_SQL.md](docs/EXCEL_TO_SQL.md).

## Four words you'll meet

| Databricks | Think of it as |
|---|---|
| Notebook | A page of cells that you run from top to bottom |
| Table | A tab of data |
| Schema | A folder of tables |
| Catalog | A drive that holds the folders |

## Good to know

- **Languages.** The calculations are in SQL, because it reads closest to the Excel formulas. Python is used only to read the Excel file, draw one chart and run the checks.
- **Your own data.** The loss trend notebooks read three tables with a handful of columns. To run them on your own claims and premium tables, see [Use your own tables](docs/STEP_BY_STEP.md#use-your-own-tables).
- **Compute.** Serverless, or a cluster on Databricks Runtime 14.3 LTS or above with Unity Catalog. Tested on serverless.
- **Clean up.** Everything is created in one schema (`excel_to_notebook` unless you change it). To remove it all, including any files you uploaded to that schema: `DROP SCHEMA <catalog>.excel_to_notebook CASCADE`.

## About this example

The data in both workbooks is synthetic: no real insureds, claims or premiums. The code is a sample to learn from, provided as is, not a supported product.
