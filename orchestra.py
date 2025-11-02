# orchestra.py
import streamlit as st

def render():
    cols = st.columns(6)
    with cols[0]: st.button("Home")
    with cols[1]: st.button("Submit Deal")
    with cols[2]: st.button("Membership")
    with cols[3]: st.button("Legal")
    with cols[4]: st.button("Support")
    with cols[5]: st.button("Chat")