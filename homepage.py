# homepage.py
import streamlit as st
import numpy as np
from orchestrator import render as toolbar
from deal_ingest import parse_html_paste
from report_engine import analyze_deal
from plot_engine import plot_dual

def main():
    toolbar()
    st.title("USCAN 5.5 – STRUCTURED FINANCE COCKPIT")

    tab1, tab2 = st.tabs(["Submit Deal", "Analysis"])

    with tab1:
        text = st.text_area("Paste Deal (Email/HTML/Table)", height=200)
        uploaded_file = st.file_uploader("Or Upload XLSX", type=["xlsx"])
        
        if st.button("Process"):
            if text:
                raw = parse_html_paste(text)
            elif uploaded_file:
                import pandas as pd
                df = pd.read_excel(uploaded_file)
                raw = df.iloc[0].to_dict()
            else:
                st.error("Paste or upload")
                return

            deal = {
                "symbol": raw.get("symbol", "Unknown"),
                "spot": float(raw["spot"]),
                "strike": float(raw["strike"]),
                "premium": float(raw["premium"]),
                "vol": float(raw["vol"]) / 100,
                "KI": float(raw["KI"]),
                "KO": float(raw["KO"]),
            }
            st.session_state.deal = deal
            st.success("Deal loaded!")

    with tab2:
        if 'deal' in st.session_state:
            deal = st.session_state.deal
            st.json(deal, expanded=False)

            days = 380
            dt = days / 365
            log_ret = np.random.normal(0, deal["vol"] * np.sqrt(dt), 20_000)
            mc_prices = deal["spot"] * np.exp(log_ret)

            report = analyze_deal(deal, mc_prices)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Expected Value (EV)", f"${report['EV']}")
                st.metric("Probability of Success", report['Prob Success'])
            with col2:
                st.metric("P(KI Hit)", report['P(KI Hit)'])
                st.metric("P(KO Hit)", report['P(KO Hit)'])

            plot_dual(deal, mc_prices, report["payoff_array"])
        else:
            st.info("Submit a deal first")

if __name__ == "__main__":
    main()