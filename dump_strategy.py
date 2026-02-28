import openpyxl
import json

wb = openpyxl.load_workbook('ibrahim_guerrilla_targeting_v2.xlsx', data_only=True)
data = {}

for sheet in ['🎯 Strategy Framework', '🔎 Query Library (100+)', '🌍 Regional Discovery']:
    ws = wb[sheet]
    rows = []
    for r in ws.iter_rows(values_only=True):
        if any(r):
            rows.append(r[:10]) # Get first 10 columns
    data[sheet] = rows

with open('strategy_dump.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
print("Done dumping to strategy_dump.json")
