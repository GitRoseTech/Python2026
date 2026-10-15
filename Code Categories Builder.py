# Utility: Read an Excel file with a Codes column and a Category column,
# then output a ready-to-paste CODE_CATEGORIES dictionary for scripts.
#
# Output format:
# CODE_CATEGORIES = {
#     1: {'label': 'Category Name', 'mod': None,
#         'codes': ['97151','97152','97153']},
#     2: {'label': 'Another Category', 'mod': None,
#         'codes': ['90832','90834']},
# }

from collections import OrderedDict

# --- USER INPUT ---
# NOTE: This cluster cannot read Excel files (pyxlsb/openpyxl not available on private PyPI).
# Export the CODES sheet to CSV first: In Excel, open the file -> select the CODES sheet ->
# File -> Save As -> choose "CSV UTF-8" -> save as "Lab Codes.csv" -> upload to workspace.
csv_path = "//"     # <-- CSV export of the CODES sheet
code_column = "Code"                                 # <-- column header with procedure codes
category_column = "Category"                          # <-- column header with category descriptions

# --- PROCESSING ---
import csv

categories = OrderedDict()
with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        code = row.get(code_column, '').strip()
        cat = row.get(category_column, '').strip()
        if code and cat:
            if cat not in categories:
                categories[cat] = []
            if code not in categories[cat]:
                categories[cat].append(code)

# --- OUTPUT: formatted CODE_CATEGORIES dictionary ---
print("CODE_CATEGORIES = {")
for i, (label, codes) in enumerate(categories.items(), start=1):
    codes_str = ",".join(f"'{c}'" for c in codes)
    print(f"    {i}:  {{'label': '{label}', 'mod': None,")
    print(f"         'codes': [{codes_str}]}},")
print("}")

# Insert the CODE_CATEGORIES generated above into a specific cell of another notebook.
# Uses the Databricks SDK Workspace API to export/import the notebook (direct file open
# is not supported for managed notebook objects on USER_ISOLATION clusters).
# Refresh the target notebook tab to see the changes.

import json, re, base64
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import ExportFormat, ImportFormat, Language

# --- USER INPUT ---
target_notebook_path = "/Workspace/Users/"  # <-- full workspace path
target_cell_number = 2                                  # <-- cell number (1-indexed)

# --- BUILD CODE_CATEGORIES TEXT FROM CELL 1 OUTPUT ---
code_cat_lines = ["CODE_CATEGORIES = {"]
for i, (label, codes) in enumerate(categories.items(), start=1):
    codes_str = ", ".join(f"'{c}'" for c in codes)
    code_cat_lines.append(f"    {i}:  {{'label': '{label}', 'mod': None,")
    code_cat_lines.append(f"         'codes': [{codes_str}]}},")
code_cat_lines.append("}")
code_categories_text = "\n".join(code_cat_lines)

# --- EXPORT NOTEBOOK VIA WORKSPACE API ---
w = WorkspaceClient()
resp = w.workspace.export(path=target_notebook_path, format=ExportFormat.JUPYTER)
nb_content = base64.b64decode(resp.content).decode('utf-8')
nb = json.loads(nb_content)

total_cells = len(nb.get('cells', []))
cell_idx = target_cell_number - 1

if cell_idx < 0 or cell_idx >= total_cells:
    raise ValueError(f"Cell {target_cell_number} out of range. Notebook has {total_cells} cells.")

# Get the existing cell source as a single string
cell_source_list = nb['cells'][cell_idx].get('source', [])
existing_source = ''.join(cell_source_list)

print(f"Target cell {target_cell_number} current length: {len(existing_source)} chars")

# Replace CODE_CATEGORIES block if it exists, otherwise append
if 'CODE_CATEGORIES' in existing_source:
    # Find start and end of CODE_CATEGORIES = { ... } using brace matching
    start_match = re.search(r'^(CODE_CATEGORIES\s*=\s*\{)', existing_source, re.MULTILINE)
    if start_match:
        start_pos = start_match.start()
        # Count braces to find the matching closing brace
        depth = 0
        end_pos = start_match.end()
        for i in range(start_match.end() - 1, len(existing_source)):
            if existing_source[i] == '{':
                depth += 1
            elif existing_source[i] == '}':
                depth -= 1
                if depth == 0:
                    end_pos = i + 1
                    break
        new_source = existing_source[:start_pos] + code_categories_text + existing_source[end_pos:]
    else:
        new_source = existing_source.rstrip() + "\n\n" + code_categories_text + "\n"
else:
    new_source = existing_source.rstrip() + "\n\n" + code_categories_text + "\n"

# Write back as a list of lines (ipynb format)
nb['cells'][cell_idx]['source'] = [line + '\n' for line in new_source.split('\n')]
if nb['cells'][cell_idx]['source']:
    nb['cells'][cell_idx]['source'][-1] = nb['cells'][cell_idx]['source'][-1].rstrip('\n')

# --- IMPORT UPDATED NOTEBOOK BACK ---
import_content = base64.b64encode(json.dumps(nb).encode('utf-8')).decode('utf-8')
w.workspace.import_(path=target_notebook_path, content=import_content, format=ImportFormat.JUPYTER, overwrite=True, language=Language.PYTHON)

print(f"\n\u2713 CODE_CATEGORIES inserted into cell {target_cell_number} of '{target_notebook_path}'")
print(f"  {len(categories)} categories, {sum(len(c) for c in categories.values())} total codes")
print(f"\n  Refresh the '{target_notebook_path.split('/')[-1]}' tab to see the update.")
