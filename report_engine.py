# report_engine.py
import numpy as np

def analyze_deal(deal, mc_prices):
    S = mc_prices
    strike = deal["strike"]
    ki = deal["KI"]
    ko = deal["KO"]
    premium = deal["premium"]

    payoff = premium - np.where(
        (S >= ko) | (S > ki),
        0,
        np.maximum(strike - S, 0)
    )

    ev = np.mean(payoff)
    prob_success = np.mean(payoff >= premium * 0.9)  # 90% of max profit
    prob_ki = np.mean(S <= ki)
    prob_strike = np.mean(S <= strike)
    prob_ko = np.mean(S >= ko)

    return {
        "EV": round(ev, 2),
        "Prob Success": f"{prob_success:.1%}",
        "P(KI Hit)": f"{prob_ki:.1%}",
        "P(Strike Hit)": f"{prob_strike:.1%}",
        "P(KO Hit)": f"{prob_ko:.1%}",
        "payoff_array": payoff
    }