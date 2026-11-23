# Presenter walkthrough: parts 1 and 2 in about seven minutes

For someone showing this to a group of actuaries. It says what to show, what to change, what to say, and what the audience should see.

**The one message:** you keep your method. What you calculate in Excel, you can calculate here with the same logic, change it yourself, and afterwards show exactly what produced every number.

## Before you present

1. Run `1_simple_101/simple_101` once, so the data is as delivered.
2. Clear old versions, if there are any: run the three `DROP TABLE` statements under "To start this part again" in [STEP_BY_STEP.md](STEP_BY_STEP.md#part-2--indication-and-versions), and delete the folder `saved_versions`.
3. Open `2_indication_and_versions/1_indication` and click **Run all**, so the boxes appear and the result shows +3.8%. Leave **save_as** empty.
4. Open these in tabs: `simple_101.xlsx` in Excel on the **Indication** tab, `1_indication`, `2_a_month_later`, `3_compare_and_reproduce`.

## The walkthrough

| Time | Show and do | Say | They should see |
|---|---|---|---|
| 0:00 | Excel, **Indication** tab. Point at the yellow cells and at `B15` | "A small indication: three assumptions, a trend, a target loss ratio. It's simplified on purpose." | +3.8% in `B15` |
| 0:45 | `1_indication`. Scroll from the top: the data, the assumptions, step 1, step 2 | "The same calculation, top to bottom. The Excel formula is written beside each line." | The same +3.8% |
| 1:45 | Type `October indications` in **save_as** and `First run` in **what_changed**. Click **Run all** | "This is Save As. It keeps the data, the assumptions, the results and the formulas together." | `Saved as version 1: October indications` |
| 2:30 | In **The assumptions**, change `0.05` to `0.06`. **Run all** | "Change an assumption as you would change a yellow cell." | +7.8% |
| 3:15 | In **Step 1**, remove the two dashes before `WHERE accident_year >= 2023`. **Run all** | "Now a change of method: the last three years only. No ticket, no developer. It's your formula." | +5.0%, and the message that October is never overwritten |
| 4:00 | **save_as**: `November indications`. **what_changed**: `Trend 6%, last three years only`. **Run all** | "Save it as the next version, with a note of what changed." | `Saved as version 2` |
| 4:30 | `2_a_month_later`: **Run all**. Back in `1_indication`: **Run all**. Save as `December indications` | "A month later the data has moved. Same formulas, different answer." | +14.9%, `Saved as version 3` |
| 5:30 | `3_compare_and_reproduce`: **Run all**. Show sections 1 and 2 | "What did I calculate, and what changed between October and November? Two lines of the calculation, shown here." | Three versions listed. The two changed lines |
| 6:15 | Open `saved_versions/v1_October_indications`. **Run all**. Show the last cell | "Can I reproduce October? The data has changed and the formulas have changed. October still gives October's number." | `Reproduced: the same result.` (+3.8%) |
| 7:00 | Close | "It's like keeping your old workbooks, except each one carries its data and its formulas with it." | |

## Questions you're likely to get

| Question | Answer |
|---|---|
| Where is the old data kept? | In the table `indication_saved_inputs`, a full copy under each version number. It doesn't depend on the live table |
| Where are the old formulas kept? | Twice: as a notebook you can open in `saved_versions`, and as text in the table `indication_versions` |
| Can someone overwrite a saved version? | The notebook refuses to save under an existing name. Who may change the tables themselves is set with permissions in Unity Catalog |
| Which version went out? | Section 3 of `3_compare_and_reproduce` marks one version as published and shows it |
| Do I have to learn Python? | No. The calculation is SQL. The one Python cell does the saving, and you don't need to read it |
| Is this the real indication method? | No. It's a teaching example. Part 3 does a real-size loss trend workbook the same way |
| What about Git, approvals, scheduled runs? | They exist and can come later. None is needed for this |

## If you have more time

Show part 3 (`3_loss_trend`): the same route on a real-size workbook, ending with "232 numbers compared with the workbook, 0 different".
