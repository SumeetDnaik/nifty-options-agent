import pandas as pd

REQUIRED = {"strike", "call_oi", "put_oi", "call_ltp", "put_ltp"}

def analyze_market(spot, prev_close, high, low, vix=0):
    change = spot - prev_close
    pct = (change / prev_close * 100) if prev_close else 0.0
    pivot = (high + low + spot) / 3
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    r2 = pivot + (high - low)
    if pct > 0.5 and spot >= pivot:
        bias = "Bullish-leaning"
    elif pct < -0.5 and spot <= pivot:
        bias = "Bearish-leaning"
    else:
        bias = "Mixed / wait"
    levels = {"Pivot": pivot, "R1": r1, "S1": s1}
    scenarios = [
        ("Bullish scenario", f"A sustained break above the session high ({high:,.2f}) with volume confirmation may support evaluating a CE setup; invalidate if price falls back into the range."),
        ("Bearish scenario", f"A break below the session low ({low:,.2f}) with follow-through may support evaluating a PE setup; invalidate if price reclaims the breakdown level."),
        ("No-trade scenario", "If price stays inside the range or option-chain data is stale, wait rather than forcing a trade.")
    ]
    if vix > 0:
        scenarios.append(("Volatility note", f"Entered India VIX: {vix:.2f}. This is user-supplied; higher volatility can mean higher premiums and faster reversals."))
    return {"change": change, "change_pct": pct, "bias": bias, "levels": levels, "scenarios": scenarios}

def load_sample_data():
    # Synthetic values for UI testing only; not real NSE quotes.
    return pd.DataFrame([
        {"strike": 22300, "call_oi": 12000, "put_oi": 28000, "call_ltp": 255.0, "put_ltp": 42.0},
        {"strike": 22400, "call_oi": 18000, "put_oi": 35000, "call_ltp": 190.0, "put_ltp": 60.0},
        {"strike": 22500, "call_oi": 42000, "put_oi": 31000, "call_ltp": 138.0, "put_ltp": 95.0},
        {"strike": 22600, "call_oi": 50000, "put_oi": 22000, "call_ltp": 91.0, "put_ltp": 145.0},
        {"strike": 22700, "call_oi": 33000, "put_oi": 14000, "call_ltp": 57.0, "put_ltp": 205.0},
    ])

def analyze_option_chain(df, spot):
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError("CSV is missing required columns: " + ", ".join(sorted(missing)))
    data = df.copy()
    for col in REQUIRED:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data = data.dropna(subset=["strike", "call_oi", "put_oi"])
    if data.empty:
        raise ValueError("No valid rows found. Check the CSV column names and values.")
    call_total, put_total = data["call_oi"].sum(), data["put_oi"].sum()
    pcr = (put_total / call_total) if call_total else None
    call_wall = float(data.loc[data["call_oi"].idxmax(), "strike"])
    put_wall = float(data.loc[data["put_oi"].idxmax(), "strike"])
    if pcr is None:
        interpretation = "Call OI is zero or missing; PCR cannot be calculated reliably."
    elif pcr > 1.2:
        interpretation = "Put OI exceeds call OI across the uploaded strikes. This is not a standalone bullish signal."
    elif pcr < 0.8:
        interpretation = "Call OI exceeds put OI across the uploaded strikes. This is not a standalone bearish signal."
    else:
        interpretation = "PCR is in a middle range. Confirm price action, change in OI, liquidity and timestamp."
    data["distance_from_spot"] = data["strike"] - spot
    table = data.sort_values("strike")
    return {"pcr": pcr, "call_wall": call_wall, "put_wall": put_wall, "interpretation": interpretation, "table": table}
