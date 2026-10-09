import streamlit as st
import pandas as pd
from analyzer import analyze_market, analyze_option_chain, load_sample_data

st.set_page_config(page_title="NIFTY Options Agent", page_icon="📈", layout="wide")
st.title("📈 NIFTY 50 Intraday Options Analysis Agent")
st.caption("Educational decision-support prototype · No auto-trading · Verify all data before acting")
st.warning("This starter version does not fetch live NSE data automatically. Upload a fresh option-chain CSV, or use clearly labelled synthetic sample data to test the dashboard.")

with st.sidebar:
    st.header("Market inputs")
    spot = st.number_input("Current NIFTY spot", min_value=0.0, value=22520.45, step=10.0)
    prev_close = st.number_input("Previous close", min_value=0.0, value=22231.80, step=10.0)
    day_high = st.number_input("Session high", min_value=0.0, value=22580.75, step=10.0)
    day_low = st.number_input("Session low", min_value=0.0, value=22294.75, step=10.0)
    vix = st.number_input("India VIX (0 if unknown)", min_value=0.0, value=0.0, step=0.5)
    timestamp = st.text_input("Data timestamp (IST)", placeholder="e.g. 12-Oct-2026 09:25")

uploaded = st.file_uploader("Upload option-chain CSV", type=["csv"])
use_sample = st.checkbox("Use included SAMPLE data (not live)", value=uploaded is None)
if uploaded is not None:
    try:
        chain = pd.read_csv(uploaded)
        source_label = "Uploaded CSV — verify source, expiry and timestamp"
    except Exception as exc:
        st.error(f"Could not read CSV: {exc}")
        chain, source_label = pd.DataFrame(), "Invalid upload"
elif use_sample:
    chain, source_label = load_sample_data(), "SYNTHETIC SAMPLE DATA — not live market data"
else:
    chain, source_label = pd.DataFrame(), "No option-chain data loaded"

market = analyze_market(spot, prev_close, day_high, day_low, vix)
cols = st.columns(4)
cols[0].metric("NIFTY input", f"{spot:,.2f}")
cols[1].metric("Change vs close", f"{market['change']:+,.2f}", f"{market['change_pct']:+.2f}%")
cols[2].metric("Session range", f"{day_low:,.2f} – {day_high:,.2f}")
cols[3].metric("Rule-based bias", market["bias"])
if timestamp:
    st.caption(f"User-entered data timestamp: {timestamp} IST. The app does not independently verify it.")

st.subheader("Calculated reference levels")
level_cols = st.columns(4)
for col, (label, value) in zip(level_cols, market["levels"].items()):
    col.metric(label, f"{value:,.2f}")

st.subheader("Option-chain analysis")
st.caption(f"Data status: {source_label}")
if not chain.empty:
    try:
        result = analyze_option_chain(chain, spot)
        a, b, c = st.columns(3)
        a.metric("PCR (OI)", f"{result['pcr']:.2f}" if result["pcr"] is not None else "Unavailable")
        b.metric("Highest call OI strike", str(result["call_wall"]) if result["call_wall"] is not None else "Unavailable")
        c.metric("Highest put OI strike", str(result["put_wall"]) if result["put_wall"] is not None else "Unavailable")
        st.write("**Interpretation (not a signal):**", result["interpretation"])
        st.dataframe(result["table"], use_container_width=True, hide_index=True)
    except ValueError as exc:
        st.error(str(exc))
else:
    st.info("Upload a CSV with columns: strike, call_oi, put_oi, call_ltp, put_ltp")

st.subheader("Conditional scenarios")
for title, detail in market["scenarios"]:
    st.markdown(f"**{title}** — {detail}")

st.subheader("Risk checklist")
st.markdown("""
- Do not trade if data is stale, timestamps differ, expiry is unclear or the bid/ask spread is wide.
- Set a maximum rupee loss before entering; include brokerage, taxes and slippage.
- Option buyers can lose the entire premium; option sellers can face much larger losses.
- This app does not place orders or connect to a broker.
- Signals are rules-based educational scenarios, not a guarantee of profit or investment advice.
""")
st.caption("Always confirm the current expiry, lot size, liquidity and applicable exchange/broker rules before trading.")
