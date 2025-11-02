# xlsx_ingest.py
import pandas as pd

def parse_xlsx(file):
    df = pd.read_excel(file)
    return df.to_dict('records')