import subprocess
import sys

def install_and_import():
    try:
        import docx
        import pandas as pd
        import openpyxl
    except ImportError:
        print("Menginstal dependency...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx", "openpyxl", "pandas"])
        import docx
        import pandas as pd

install_and_import()
import docx
import pandas as pd

print("========== CAPSTONE PLAYBOOK ==========")
try:
    doc = docx.Document(r"C:\Users\monar\Downloads\[Pijak] Capstone Playbook.docx")
    for para in doc.paragraphs:
        if para.text.strip():
            print(para.text)
except Exception as e:
    print("Gagal membaca DOCX:", e)

print("\n========== RUBRIK PENILAIAN ==========")
try:
    # Coba baca semua sheet
    xls = pd.ExcelFile(r"C:\Users\monar\Downloads\Rubrik Penilaian Capstone Project.xlsx")
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    
    for sheet_name in xls.sheet_names:
        print(f"\n--- SHEET: {sheet_name} ---")
        df = pd.read_excel(xls, sheet_name=sheet_name)
        print(df.dropna(how='all'))
except Exception as e:
    print("Gagal membaca XLSX:", e)
