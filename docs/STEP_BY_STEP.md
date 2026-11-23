# Step by step

Follow this from top to bottom. Each step says what to click and what you should see.

- [Before you start](#before-you-start)
- [Get the files into Databricks](#get-the-files-into-databricks)
- [Part 1 · Simple 101](#part-1--simple-101)
- [Part 2 · Loss trend](#part-2--loss-trend)
- [Part 3 · Unity Catalog function](#part-3--unity-catalog-function)
- [Use your own tables](#use-your-own-tables)
- [Use your own Excel file](#use-your-own-excel-file)
- [If something goes wrong](#if-something-goes-wrong)

## Before you start

You need:

- A Databricks workspace with Unity Catalog.
- A **catalog** where you can create a schema. Most workspaces have a default one, and the notebooks use it. If yours doesn't allow it, ask your workspace admin for either "a catalog where I can create a schema" or "a schema where I can create tables and functions".
- Compute: serverless, or a cluster on Databricks Runtime 14.3 LTS or above.
- Excel, to look at the two workbooks next to the notebooks. This is optional but helps.

Everything the notebooks create goes into one schema, called `excel_to_notebook`.

## Get the files into Databricks

1. In Databricks, click **Workspace** in the left menu.
2. Click **Create → Git folder** (top right).
3. In **Git repository URL**, paste `https://github.com/wryszka/excel-to-notebook`.
4. Click **Create Git folder**. The repository is public, so no GitHub login is needed.

You now have a folder `excel-to-notebook` with three numbered folders inside.

To look at the workbooks in Excel, download them from GitHub: open the file on the GitHub page and click **Download raw file**.

## Part 1 · Simple 101

**The spreadsheet.** `simple_101.xlsx` has three tabs: **Claims** (60 claims), **Premium** (5 years) and **Summary** (formulas).

**The notebook.**

1. Open `1_simple_101/simple_101`.
2. Click **Run all** (top right). If asked for compute, choose **Serverless**.

Two boxes appear at the top of the notebook: **catalog** and **schema**. They show where the tables went. To use another catalog or schema, type its name in the box and click **Run all** again. Use the same values in every notebook.

**What you should see.**

| Step in the notebook | Result |
|---|---|
| 1 · Read the tabs | The 60 claims, as in the Claims tab |
| 2 · Save them as tables | No output. The tables `simple_claims` and `simple_premium` now exist |
| 3 · The Summary tab, as one query | Five rows, 2021 to 2025. For 2021: 11 claims, incurred 135,100, loss ratio 0.3295 |
| 4 · Check against the spreadsheet | `25 numbers compared with the Summary tab. Largest difference: 0.000000` |

**Look at the tables.** Click **Catalog** in the left menu, open your catalog, then the schema `excel_to_notebook`. Click `simple_summary`, then **Sample Data**.

**The point.** Step 3 is the whole Summary tab. Each line of the query has the Excel formula it replaces written next to it.

## Part 2 · Loss trend

**The spreadsheet.** `LossTrend_PL_US_AY2015plus_v4_FINAL.xlsx` is a loss trend study for a professional liability book, accident years 2015 to 2026, valued at 30 September 2026. It has 2,949 claims and 9,026 loss rows.

**The notebooks.** Open the folder `2_loss_trend` and run the five notebooks in order: open each one and click **Run all**.

| Notebook | Replaces these tabs | What you should see |
|---|---|---|
| `1_load_the_workbook` | Claims, Loss Data, Premium Data | `Claims: 2,949 rows saved as lt_claims`, `Loss Data: 9,026 rows saved as lt_loss_data`, `Premium Data: 846 rows saved as lt_premium_data` |
| `2_triangles` | Triangle; Freq & Severity Triangles | Two triangles. First incurred cell (2015, age 12): 6,274,065. First claims cell: 112 |
| `3_development_factors` | The "Vol-weighted" rows; LDF Selections | Factors from the data (claims 12 to 24: 1.717). One pick saved (1.650, with a reason). Claims factor to ultimate at 12 months: 2.140 |
| `4_trend` | Frequency Trend; Severity Trend | Ultimate frequency and severity by year, a chart, and the fits. Frequency: 3-yr +3.4%, 5-yr +6.6%, 8-yr −1.2%, all years −1.5%. Trend picks saved |
| `5_check_against_the_workbook` | (none: it compares) | `All together: 232 numbers compared with the workbook, 0 different.` |

**The point.** Each calculation tab became one short query. The picks, which are yellow cells in Excel, are stored in tables with who, when and why.

**Versions.** Every **Run all** of notebook 3 or 4 saves the picks as a new version, even if you changed nothing. Earlier versions are never changed. The calculations always use the newest version.

**Try a change.**

1. Open `3_development_factors` and find the cell that starts `CREATE OR REPLACE TEMP VIEW my_picks`.
2. Change `1.650` to `1.700` and click **Run all**.
3. Open `4_trend` and click **Run all**.
4. Look at the last result in `4_trend`: the newest version of the trend picks shows, in `ldf_version`, the newest version of the factors.

To see every factor selection: `SELECT * FROM lt_ldf_selection ORDER BY version, age_from`.

After this change, notebook 5 will report differences. That's correct: the workbook still holds 1.650.

## Part 3 · Unity Catalog function

Do this after parts 1 and 2: it uses their tables.

1. Open `3_unity_catalog_function/make_it_a_function`.
2. Click **Run all**.

**What you should see.**

| Step in the notebook | Result |
|---|---|
| 1 · A function that returns one number | `loss_ratio` is created, then used: the same loss ratios as the Summary tab |
| 2 · A function that returns a table | `trend_fit` is created, then `SELECT * FROM trend_fit(4)` gives the 4-year trend, a window the workbook doesn't have |
| 3 · Where it lives | The description of `trend_fit` |

**Look at the functions.** Click **Catalog**, open your schema, and look under **Functions**.

**The point.** A function is a formula with a name, stored next to the tables. Start with notebook cells. Make a function when more than one notebook or person needs the same formula.

## Use your own tables

The loss trend notebooks 2 to 4 read only three tables, and only these columns:

| Table | Columns used | Meaning |
|---|---|---|
| `lt_claims` | `accident_year`, `report_age_months` | One row for each claim |
| `lt_loss_data` | `accident_year`, `dev_age_months`, `incurred` | One row for each loss transaction: the movement, not a running total. `incurred` = paid + change in case reserve |
| `lt_premium_data` | `calendar_year`, `earned_exposure` | Earned exposure. It can be monthly rows: the notebook adds them up by year |

`report_age_months` and `dev_age_months` are months since 1 January of the accident year, rounded up to a multiple of 12. A claim from accident year 2020 reported in March 2021 has `report_age_months` = 24.

So you don't load the workbook. You create three views with those column names, in a new schema, and run notebooks 2 to 4 on them.

1. Open a new notebook (or the SQL editor). Paste the template below, replace `my_catalog`, the table names and the column names with yours, and run it.
2. Open `2_triangles`. Run the first code cell so the boxes appear. Type your catalog in **catalog** and `loss_trend` in **schema**. Change the valuation date in the first line of the query. Click **Run all**.
3. Open `3_development_factors`, set the same two boxes, and replace the example pick with your own before you run. For no picks, use `(12, NULL, NULL, NULL)`.
4. Open `4_trend`, set the same two boxes, replace the example trend picks, and run.

```sql
CREATE SCHEMA IF NOT EXISTS my_catalog.loss_trend;

CREATE OR REPLACE VIEW my_catalog.loss_trend.lt_claims AS
SELECT year(loss_date) AS accident_year,
       ceil(((year(report_date) - year(loss_date)) * 12 + month(report_date)) / 12) * 12 AS report_age_months
FROM my_catalog.my_schema.my_claims_table;

CREATE OR REPLACE VIEW my_catalog.loss_trend.lt_loss_data AS
SELECT year(loss_date) AS accident_year,
       ceil(((year(transaction_date) - year(loss_date)) * 12 + month(transaction_date)) / 12) * 12 AS dev_age_months,
       paid_amount + reserve_change AS incurred
FROM my_catalog.my_schema.my_claim_transactions_table;

CREATE OR REPLACE VIEW my_catalog.loss_trend.lt_premium_data AS
SELECT year(earning_month) AS calendar_year, earned_exposure
FROM my_catalog.my_schema.my_earned_premium_table;
```

Things to know on your own data:

- Notebook 5 compares with the example workbook, so skip it.
- The latest accident year is always shown but left out of the trend fits.
- An accident year with no exposure rows is left out of the results.
- The triangle has ages 12 to 144 months, which fits 12 accident years. For more, change `144` in the two lines with `sequence(12, 144, 12)` (one in `2_triangles`, one in `3_development_factors`) and add the extra ages to the two `PIVOT` lists in `2_triangles`.

## Use your own Excel file

1. In Databricks, click **Catalog**, open your schema, and click **Create → Volume**. A volume is a folder for files.
2. Open the volume and click **Upload to this volume**. Upload your workbook.
3. Click the file's menu and **Copy path**. It looks like `/Volumes/<catalog>/<schema>/<volume>/my_file.xlsx`.
4. In `simple_101` or `1_load_the_workbook`, find the line that starts `workbook =`. Put your path there in place of the file name, and change the tab names in that cell to yours.

The check at the end compares with the example workbook, so it won't apply to your file.

## If something goes wrong

| What you see | What to do |
|---|---|
| An error on the **Where to work** cell that mentions the catalog or schema (not found, or permission denied) | Type a catalog you can write to in the **catalog** box at the top, and click **Run all** again. If you were given a schema instead, type its name in **schema** too |
| The **catalog** box shows `hive_metastore` | Type the name of a Unity Catalog catalog instead, and run again |
| `TABLE_OR_VIEW_NOT_FOUND` | Run the earlier notebooks first, in order, with the same catalog and schema |
| `No such file` for the `.xlsx` | The notebook must stay in the same folder as its workbook. Create the Git folder again rather than copying a notebook alone |
| `%pip install openpyxl` fails | Your workspace can't reach the Python package index. Ask your admin how to install the `openpyxl` library |
| The Git folder can't be created from the URL | Your workspace may limit which Git addresses are allowed. Ask your admin to allow it, or download the repository as a ZIP from GitHub and use **Workspace → Import** |
| Notebook 5 reports differences | You changed a pick (see **Try a change**). To go back to the workbook's numbers, set the pick back to `1.650` and run 3, 4 and 5 again |
| You want to start again | Run `DROP SCHEMA <catalog>.excel_to_notebook CASCADE` in any notebook or the SQL editor, then run the notebooks again. This also deletes files you uploaded to a volume in that schema |
