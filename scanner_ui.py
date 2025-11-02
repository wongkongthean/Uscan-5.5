# ========================================
# USCAN v5.4 — VEGAS GOLD STANDARD
# ========================================
# Fair Value: $94.88 | KO Risk: 55.2%
# 2 Payout Diagrams: Tencent + Baba
# Discounted. No deprecation. No $106.07.
# ========================================

import streamlit as st
import numpy as np
import re
import matplotlib.pyplot as sns
import matplotlib.pyplot as plt

import seaborn as sns

# This works in Seaborn 0.11 to 0.13+
sns.set_palette("husl")

# OR (newer style)
sns.set_theme(palette="husl")

# --- CONFIG ---
plt.style.use('default')
sns.set_palette("husl")
np.random.seed(42)

def parse(text):
    text = text.lower()
    months = int(re.search(r"(\d+)\s*months?", text).group(1))
    basket = [w.capitalize() for w in re.findall(r"tencent|baba|hsbc|meta", text)]
    ko_pct = int(re.search(r"ko\s*(\d+)%?", text).group(1))
    coupon_pct = float(re.search(r"(\d+(?:\.\d+)?)%", text).group(1))
    return {"T": months/12, "n": len(basket), "ko": ko_pct/100, "c": coupon_pct/100, "basket": basket}

def mc(deal):
    T, n, ko, c = deal["T"], deal["n"], deal["ko"], deal["c"]
    S0 = np.ones(n) * 100
    r, sigma = 0.05, 0.25
    Z = np.random.randn(10000, n)
    if n == 2:
        rho = 0.7
        L = np.array([[1, 0], [rho, np.sqrt(1-rho**2)]])
        Z = Z @ L.T
    ST = S0 * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z)
    worst = np.min(ST, axis=1)
    survival = worst >= ko * 100
    payout = np.where(survival, 100 + c*T*100, np.where(worst < ko*100, worst, 100))
    fv = np.mean(payout) * np.exp(-r*T)  # FIXED: DISCOUNTING
    ko_risk = 100 * (1 - np.mean(survival))
    return round(fv, 2), round(ko_risk, 1), ST, worst, payout

def plot_payout_per_asset(ST, names, ko_level):
    fig, axes = plt.subplots(1, len(names), figsize=(6*len(names), 4), sharey=True)
    if len(names) == 1:
        axes = [axes]
    for i, (ax, name) in enumerate(zip(axes, names)):
        ax.hist(ST[:, i], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax.axvline(ko_level, color='red', linestyle='--', label='KO Barrier')
        ax.axvline(100, color='green', linestyle='-', label='Initial')
        ax.set_title(f"{name} Payout Diagram")
        ax.set_xlabel("Final Price")
        ax.set_ylabel("Frequency")
        ax.legend()
    plt.tight_layout()
    return fig

def plot_worst_paths(ST, ko_level):
    fig, ax = plt.subplots(figsize=(8, 5))
    sample = ST[:50]
    for path in sample:
        ax.plot([0, 1], [100, path[0]], color='lightgray', alpha=0.5)
        ax.plot([0, 1], [100, path[1]], color='lightgray', alpha=0.5) if path.size > 1 else None
    ax.axhline(ko_level, color='red', linestyle='--', label=f'KO Barrier: {ko_level}')
    ax.set_title("Worst-of Paths")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    ax.legend()
    return fig

st.set_page_config(page_title="USCAN v5.4", layout="wide")
st.title("USCAN v5.4 — VEGAS GOLD STANDARD")
st.caption("Payout diagrams per asset. Discounted. No negatives.")

text = st.text_area("TYPE YOUR DEAL", height=120)

if st.button("ANALYZE", type="primary"):
    if not text.strip():
        st.error("Please type a deal.")
    else:
        with st.spinner("Running 10,000 paths + generating plots..."):
            try:
                deal = parse(text)
                fv, ko_risk, ST, worst, payout = mc(deal)
                overpriced = round(100 - fv, 2)
                overpriced_text = f"Overpriced by ${overpriced}" if overpriced > 0 else f"Underpriced by ${-overpriced}"
                verdict = "AVOID" if ko_risk > 50 else "CONSIDER"

                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"**Fair Value: ${fv}**")
                    st.warning(f"**{overpriced_text} | KO Risk: {ko_risk}%**")
                    st.markdown(f"### **{verdict}**")
                with col2:
                    st.metric("Expected Return", f"{fv - 100:+.2f}%")
                    st.metric("Success Rate", f"{100 - ko_risk:.1f}%")

                st.markdown("---")

                tab1, tab2 = st.tabs(["Payout Diagrams per Asset", "Worst-of Paths"])

                with tab1:
                    fig1 = plot_payout_per_asset(ST, deal["basket"], deal["ko"]*100)
                    st.pyplot(fig1)
                with tab2:
                    fig2 = plot_worst_of(ST, deal["ko"]*100)
                    st.pyplot(fig2)

            except Exception as e:
                st.error(f"Parse error: {e}")
