# deal_ingest.py
import streamlit as st
from bs4 import BeautifulSoup
import re

def parse_paste(text):
    soup = BeautifulSoup(text, 'html.parser')
    tables = soup.find_all('table')
    if tables:
        # Use pandas
        import pandas as pd
        df = pd.read_html(str(tables[0]))[0]
        return df.to_dict('records')[0]
    else:
        # AI fallback
        prompt = f"Extract: symbol, spot, strike, premium, vol, KI%, KO% from:\n{text}"
        return st.session_state.grok.ask(prompt)  # future