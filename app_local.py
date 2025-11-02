# UScan\app\app_local.py  ← USE THIS LOCALLY
import streamlit as st
import sys
import os

# Fix IDE import issues
sys.path.append(os.path.dirname(__file__))

from homepage import main

st.set_page_config(page_title="UScan 5.5", layout="wide")
main()
