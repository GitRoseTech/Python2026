# Python2026

Code Categories Builder
Builds and injects a CODE_CATEGORIES dictionary into a target Per Capita analysis notebook from a CSV of procedure codes.

How to Use
Prepare your CSV — Export the CODES sheet from your Excel file as CSV UTF-8 (this cluster cannot read .xlsx directly). The CSV must have at least two columns: one for procedure codes and one for category names.
Upload the CSV — Drag the file into your Databricks workspace.
Update the inputs in Cell 1 (see below), then Run Cell 1. It reads the CSV and prints the formatted CODE_CATEGORIES dictionary so you can review it.
Update the inputs in Cell 2 (see below), then Run Cell 2. It injects the dictionary directly into the target notebook cell, replacing any existing CODE_CATEGORIES block.
Refresh the target notebook tab to see the updated code.
Inputs to Change
Cell 1 — CSV source settings:

Variable	What to set	Example
csv_path	Full workspace path to your uploaded CSV	"/Workspace/Users/"
code_column	Column header containing the procedure codes	"Code"
category_column	Column header containing the category labels	"Category"
Cell 2 — Target notebook settings:

Variable	What to set	Example
target_notebook_path	Full workspace path of the notebook to update	"/Workspace/Users"
target_cell_number	Cell number (1-indexed) where CODE_CATEGORIES lives	2
