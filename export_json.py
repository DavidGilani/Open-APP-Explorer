import gspread
import json
from google.oauth2.service_account import Credentials

CREDENTIALS_FILE = r"C:\Users\David278\credentials.json"
SHEET_ID = "1jH2blZLjztpLqAgh7BV7G-Kl7TI1_PZZxojEY2lH5Zg"
OUTPUT_FILE = r"C:\Users\David278\Open-APP-Explorer\data.json"

def get_sheets_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    return gspread.authorize(creds)

def parse_num(val):
    if val is None or val == '':
        return None
    try:
        return float(str(val).replace('%','').strip())
    except:
        return None

def parse_int(val):
    if val is None or val == '':
        return None
    try:
        return int(float(str(val).strip()))
    except:
        return None

def main():
    print("Connecting to Google Sheets...")
    gc = get_sheets_client()
    ss = gc.open_by_key(SHEET_ID)

    # ── APPs tab ──────────────────────────────────────────────────────────
    print("Reading APPs tab...")
    register = ss.worksheet("APPs")
    r_rows = register.get_all_values()
    url_by_ukprn = {}
    past_url_by_ukprn = {}
    for row in r_rows[1:]:
        ukprn    = row[0].strip() if len(row) > 0 else ''
        url      = row[3].strip() if len(row) > 3 else ''
        past_url = row[4].strip() if len(row) > 4 else ''
        if ukprn and url.startswith('http'):
            url_by_ukprn[ukprn] = url
        if ukprn and past_url.startswith('http'):
            past_url_by_ukprn[ukprn] = past_url

    # ── Institutions tab ──────────────────────────────────────────────────
    print("Reading Institutions tab...")
    inst_sheet = ss.worksheet("Institutions")
    i_rows = inst_sheet.get_all_values()
    inst_by_ukprn = {}
    for row in i_rows[1:]:
        def g(idx):
            return row[idx].strip() if idx < len(row) else ''
        ukprn = g(0)
        if not ukprn:
            continue
        inst_by_ukprn[ukprn] = {
            "mission_group":  g(2),
            "mission_group2": g(3),
            "region":         g(4),
            "mature_pct":     parse_num(g(5)),
            "imd_q1":         parse_num(g(6)),
            "imd_q2":         parse_num(g(7)),
            "imd_q3":         parse_num(g(8)),
            "imd_q4":         parse_num(g(9)),
            "imd_q5":         parse_num(g(10)),
            "disability":     parse_num(g(11)),
            "asian":          parse_num(g(12)),
            "black":          parse_num(g(13)),
            "mixed":          parse_num(g(14)),
            "other_eth":      parse_num(g(15)),
            "white":          parse_num(g(16)),
            "gem":            parse_num(g(17)),
            "fsm":            parse_num(g(18)),
            "uk_pct":         parse_num(g(19)),
            "alevel":         parse_num(g(20)),
            "btec":           parse_num(g(21)),
            "access_found":   parse_num(g(22)),
            "male":           parse_num(g(23)),
            "lgb":            parse_num(g(24)),
            "tundra_q1":      parse_num(g(25)),
            "tundra_q2":      parse_num(g(26)),
            "tundra_q3":      parse_num(g(27)),
            "tundra_q4":      parse_num(g(28)),
            "tundra_q5":      parse_num(g(29)),
            # Student numbers (cols 30-33)
            "total_ft_ug":          parse_int(g(30)),
            "total_pt_ug":          parse_int(g(31)),
            "total_apprenticeship": parse_int(g(32)),
            "total_ug_students":    parse_int(g(33)),
        }

    # ── Targets tab ───────────────────────────────────────────────────────
    print("Reading Targets tab...")
    targets = ss.worksheet("Targets")
    t_rows = targets.get_all_values()
    headers = [h.lower().replace(' ','_').replace('?','').replace('/','_')
                .replace('(','').replace(')','').strip()
               for h in t_rows[0]]

    vague = {
        'other',
        'other (please specify in description)',
        'not specified (please give detail in description)',
        'not specified'
    }

    def prefer_clean(original, clean):
        if original.strip().lower() in vague and clean.strip():
            return clean.strip()
        return original.strip()

    def find_col(name):
        try:
            return headers.index(name)
        except ValueError:
            return -1

    idx_char_clean = find_col('characteristic_clean')
    idx_tg_clean   = find_col('target_group_clean')
    idx_cg_clean   = find_col('comparator_group_clean')

    def safe(row, idx):
        return row[idx].strip() if idx != -1 and idx < len(row) else ''

    output  = []
    skipped = 0

    for row in t_rows[1:]:
        def g(idx):
            return row[idx].strip() if idx < len(row) else ''

        obj = {}
        for i, h in enumerate(headers):
            obj[h] = row[i].strip() if i < len(row) else ''

        ukprn = obj.get('ukprn', '').strip()

        if not obj.get('reference_number', '').strip():
            skipped += 1
            continue

        obj['characteristic']   = prefer_clean(obj.get('characteristic', ''),   safe(row, idx_char_clean))
        obj['target_group']     = prefer_clean(obj.get('target_group', ''),     safe(row, idx_tg_clean))
        obj['comparator_group'] = prefer_clean(obj.get('comparator_group', ''), safe(row, idx_cg_clean))

        obj['plan_url']      = url_by_ukprn.get(ukprn, '')
        obj['past_plan_url'] = past_url_by_ukprn.get(ukprn, '')
        obj['current_plan']  = obj.get('current_plan', '').strip()
        inst = inst_by_ukprn.get(ukprn, {})
        for k, v in inst.items():
            obj[k] = v

        output.append(obj)

    print(f"Processed {len(output)} targets ({skipped} rows skipped)")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)

    print(f"Written to {OUTPUT_FILE}")
    size_kb = len(json.dumps(output)) / 1024
    print(f"File size: {size_kb:.0f} KB")

if __name__ == "__main__":
    main()