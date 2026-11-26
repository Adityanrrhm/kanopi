import os
import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause_screen():
    input("\nTekan [Enter] untuk melanjutkan...")

def format_currency(amount):
    return f"Rp {int(amount):,}".replace(",", ".")

def fmt_date(iso_date_str, with_time=True):
    if not iso_date_str or str(iso_date_str).strip() in ("", "nan", "None", "-"):
        return "-"
    val = str(iso_date_str).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.datetime.strptime(val, fmt)
            if fmt == "%Y-%m-%d" or not with_time:
                return dt.strftime("%d-%m-%Y")
            return dt.strftime("%d-%m-%Y %H:%M")
        except ValueError:
            continue
    return val

def parse_date_input(dd_mm_yyyy_str):
    try:
        return datetime.datetime.strptime(dd_mm_yyyy_str.strip(), "%d-%m-%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None

def clean_integer_input(text_val):
    if text_val is None:
        return None
    cleaned = str(text_val).strip().replace(".", "").replace(",", "")
    if cleaned.isdigit():
        return int(cleaned)
    return None

def generate_sequential_id(dataframe, column_name, prefix, pad_length=3):
    if dataframe.empty or column_name not in dataframe.columns:
        return f"{prefix}-{'1'.zfill(pad_length)}"
    existing_numbers = []
    for raw_id in dataframe[column_name].dropna():
        str_id = str(raw_id).strip()
        if str_id.startswith(f"{prefix}-"):
            num_part = str_id.split("-")[-1]
            if num_part.isdigit():
                existing_numbers.append(int(num_part))
    if not existing_numbers:
        return f"{prefix}-{'1'.zfill(pad_length)}"
    next_number = max(existing_numbers) + 1
    return f"{prefix}-{str(next_number).zfill(pad_length)}"
