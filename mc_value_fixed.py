# === FINAL mc_value (BROADCAST S0 TO n_paths) ===
def mc_value(struct, n_paths=10000, n_steps=1):
    np.random.seed(42)
    T = struct["maturity"]
    S0 = np.array(struct["initial_prices"])  # shape: (n,)
    n = len(S0)
    dt = T / n_steps
    drift = (0.05 - 0.5 * 0.2**2) * dt
    vol = 0.2 * np.sqrt(dt)

    # Simulate increments: (n_paths, n_steps, n)
    increments = drift + vol * np.random.randn(n_paths, n_steps, n)
    log_paths = np.cumsum(increments, axis=1)
    paths = np.exp(log_paths) * S0  # (n_paths, n_steps, n)

    # Prepend S0 to every path: S0_broadcast shape (n_paths, 1, n)
    S0_broadcast = S0.reshape(1, 1, n)  # (1, 1, n)
    S0_broadcast = np.tile(S0_broadcast, (n_paths, 1, 1))  # (n_paths, 1, n)

    # Concatenate on time axis (axis=1)
    paths = np.concatenate([S0_broadcast, paths], axis=1)  # (n_paths, n_steps+1, n)

    # Worst-of across underlyings
    worst = np.min(paths, axis=2)  # (n_paths, n_steps+1)
    ko_level = 0.98
    ko_hit = np.any(worst <= ko_level, axis=1)
    survival = ~ko_hit

    coupon = struct["other_props"][1]["coupon"]
    final_worst = worst[:, -1]
    payoff = np.where(
        survival,
        100 + coupon * T * 100,
        np.where(final_worst < ko_level, final_worst * 100, 100)
    )
    fv = np.mean(payoff) * np.exp(-0.05 * T)
    prob_no_ko = np.mean(survival)

    return {
        "fair_value_gross": round(fv, 2),
        "prob_no_ko": round(prob_no_ko * 100, 2)
    }
