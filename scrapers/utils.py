import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEL_FILE = os.path.join(ROOT_DIR, 'ibrahim_guerrilla_targeting_v2.xlsx')
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
OUTPUTS_DIR = os.path.join(ROOT_DIR, 'outputs', 'json')

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# --- Upwork sheet schema ---
UPWORK_SHEET = '🔧 Upwork Projects'
UPWORK_HEADERS = [
    '#',              # 1
    'Job Title',      # 2
    'Budget',         # 3
    'Type',           # 4  (Hourly / Fixed-price)
    'Duration',       # 5
    'Experience',     # 6
    'Skills',         # 7
    'Description',    # 8
    'Posted',         # 9
    'Job URL',        # 10
    'Status',         # 11
    'Priority',       # 12
    'Notes',          # 13
]


def save_debug_html(html_content, source_name):
    """Save raw HTML for debugging scraper selectors."""
    path = os.path.join(LOGS_DIR, f'debug_{source_name}_html.html')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html_content if html_content else '')
    print(f"[DEBUG] Saved HTML dump to {path}")


def save_debug_text(text_content, source_name):
    """Save extracted text for debugging."""
    path = os.path.join(LOGS_DIR, f'debug_{source_name}_text.txt')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text_content if text_content else '')
    print(f"[DEBUG] Saved text dump to {path}")


def save_to_json(leads, filename):
    if not leads:
        return
    path = os.path.join(OUTPUTS_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(leads, f, indent=4)
    print(f"[OK] Saved {len(leads)} leads to {path}")


def get_existing_leads():
    """Get existing company leads for deduplication."""
    if not os.path.exists(EXCEL_FILE):
        return set()

    wb = openpyxl.load_workbook(EXCEL_FILE)
    if '📋 Company Tracker' not in wb.sheetnames:
        return set()

    ws = wb['📋 Company Tracker']
    existing = set()
    for row in range(2, ws.max_row + 1):
        name = ws.cell(row=row, column=2).value
        source = ws.cell(row=row, column=13).value
        demand = ws.cell(row=row, column=14).value
        if name:
            if source and str(source).strip().lower() == 'upwork':
                demand_key = str(demand).strip().lower() if demand else ""
                existing.add(f"upwork::{demand_key}")
            else:
                existing.add(str(name).strip().lower())
    return existing


def get_existing_upwork_leads():
    """Get existing Upwork project titles for deduplication."""
    if not os.path.exists(EXCEL_FILE):
        return set()

    wb = openpyxl.load_workbook(EXCEL_FILE)
    if UPWORK_SHEET not in wb.sheetnames:
        return set()

    ws = wb[UPWORK_SHEET]
    existing = set()
    for row in range(2, ws.max_row + 1):
        title = ws.cell(row=row, column=2).value  # Job Title column
        if title:
            existing.add(str(title).strip().lower())
    return existing


def _ensure_upwork_sheet(wb):
    """Create the Upwork Projects sheet with headers if it doesn't exist."""
    if UPWORK_SHEET in wb.sheetnames:
        return wb[UPWORK_SHEET]

    ws = wb.create_sheet(UPWORK_SHEET)

    # Style the headers
    header_font = Font(bold=True, color='FFFFFF', size=11)
    header_fill = PatternFill(start_color='2F5496', end_color='2F5496', fill_type='solid')
    header_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    for col_idx, header in enumerate(UPWORK_HEADERS, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = thin_border

    # Set column widths
    widths = [5, 50, 12, 12, 18, 14, 40, 60, 16, 50, 10, 8, 30]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    return ws


def save_upwork_to_excel(leads):
    """Save Upwork leads to dedicated Upwork Projects sheet."""
    if not leads:
        return 0

    if not os.path.exists(EXCEL_FILE):
        print(f"[ERROR] Excel file not found: {EXCEL_FILE}")
        return 0

    wb = openpyxl.load_workbook(EXCEL_FILE)
    ws = _ensure_upwork_sheet(wb)

    # Find max ID
    max_id = 0
    for row in range(2, ws.max_row + 1):
        cell_val = ws.cell(row=row, column=1).value
        if isinstance(cell_val, int) and cell_val > max_id:
            max_id = cell_val

    existing = get_existing_upwork_leads()
    next_row = ws.max_row + 1
    added_count = 0

    for lead in leads:
        title = lead.get('title', '').strip()
        if len(title) < 5:
            continue

        dedup_key = title.lower()
        if dedup_key in existing:
            continue

        ws.cell(row=next_row, column=1, value=max_id + added_count + 1)     # #
        ws.cell(row=next_row, column=2, value=title)                         # Job Title
        ws.cell(row=next_row, column=3, value=lead.get('budget', ''))        # Budget
        ws.cell(row=next_row, column=4, value=lead.get('type', ''))          # Type
        ws.cell(row=next_row, column=5, value=lead.get('duration', ''))      # Duration
        ws.cell(row=next_row, column=6, value=lead.get('experience', ''))    # Experience
        ws.cell(row=next_row, column=7, value=lead.get('skills', ''))        # Skills
        ws.cell(row=next_row, column=8, value=lead.get('description', ''))   # Description
        ws.cell(row=next_row, column=9, value=lead.get('posted', ''))        # Posted
        ws.cell(row=next_row, column=10, value=lead.get('job_url', ''))      # Job URL
        ws.cell(row=next_row, column=11, value="Research")                   # Status
        ws.cell(row=next_row, column=12, value=lead.get('priority', 'A'))    # Priority
        ws.cell(row=next_row, column=13, value=lead.get('notes', ''))        # Notes

        existing.add(dedup_key)
        next_row += 1
        added_count += 1

    wb.save(EXCEL_FILE)
    return added_count


def save_to_excel(leads):
    """Save company leads (ArtStation, LinkedIn, Wamda) to Company Tracker sheet."""
    if not leads:
        return 0

    if not os.path.exists(EXCEL_FILE):
        print(f"[ERROR] Excel file not found: {EXCEL_FILE}")
        return 0

    wb = openpyxl.load_workbook(EXCEL_FILE)

    if '📋 Company Tracker' not in wb.sheetnames:
        print("[ERROR] Sheet '📋 Company Tracker' not found in Excel file.")
        return 0

    ws = wb['📋 Company Tracker']

    # Find the actual max ID in column 1
    max_id = 0
    for row in range(2, ws.max_row + 1):
        cell_val = ws.cell(row=row, column=1).value
        if isinstance(cell_val, int) and cell_val > max_id:
            max_id = cell_val

    existing = get_existing_leads()
    next_row = ws.max_row + 1
    added_count = 0

    for lead in leads:
        company_name = lead.get('company', 'Unknown').strip()
        demand_signal = lead.get('demand_signal', '')
        source = lead.get('source', '')

        # Basic cleaning
        if len(company_name) < 2 or company_name.lower() in ["sign up", "sign in", "apply", "copy link"]:
            continue

        # Deduplication
        dedup_key = company_name.lower()
        if dedup_key in existing:
            continue

        ws.cell(row=next_row, column=1, value=max_id + added_count + 1)  # #
        ws.cell(row=next_row, column=2, value=company_name)               # Company Name
        ws.cell(row=next_row, column=3, value=lead.get('country', 'Unknown'))  # Country
        ws.cell(row=next_row, column=4, value=lead.get('city', ''))            # City
        ws.cell(row=next_row, column=5, value=lead.get('category', '3D/Motion Target'))  # Category
        ws.cell(row=next_row, column=8, value=lead.get('website', ''))         # Website
        ws.cell(row=next_row, column=13, value=source or 'Master Suite')       # How Found
        ws.cell(row=next_row, column=14, value=demand_signal or 'N/A')         # Demand Signal
        ws.cell(row=next_row, column=15, value=lead.get('service_needed', '3D/Motion Design'))  # Service They Need
        ws.cell(row=next_row, column=20, value="Research")                     # Status
        ws.cell(row=next_row, column=21, value=lead.get('priority', 'A'))      # Priority
        ws.cell(row=next_row, column=23, value=lead.get('notes', ''))          # Notes

        existing.add(dedup_key)
        next_row += 1
        added_count += 1

    wb.save(EXCEL_FILE)
    return added_count
