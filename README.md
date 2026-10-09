# NIFTY 50 Intraday Options Analysis Agent

A beginner-friendly Streamlit dashboard for studying NIFTY spot levels and option-chain data. It calculates basic pivot levels, PCR (put OI / call OI), and the strikes with the highest call and put open interest.

## Important limitations
- **No automatic live NSE feed is included.** Exchange pages can use dynamic requests, rate limits, cookies or access controls. Never assume scraped data is current or reliable.
- Sample option-chain rows are synthetic and clearly labelled. Never use them for a real trade.
- The app does not execute orders and does not promise profitable signals.
- Verify live prices, expiry, lot size, liquidity and rules with NSE and your broker.

## Files
- `app.py`: dashboard
- `analyzer.py`: calculations and rule-based interpretations
- `data/sample_option_chain.csv`: synthetic sample data for testing
- `requirements.txt`: Python dependencies

## Run locally
1. Install Python 3.10 or newer.
2. In this folder run `pip install -r requirements.txt`
3. Run `streamlit run app.py`
4. Open the local URL shown in the terminal.

## Publish from an Android tablet
1. Download and extract this ZIP.
2. In your browser, create a GitHub repository.
3. Upload the project files (you may upload files individually if folder upload is inconvenient).
4. Open Streamlit Community Cloud and connect GitHub.
5. Choose your repository and set `app.py` as the main file.
6. Deploy and test using sample data before uploading real data.

## Option-chain CSV format
Upload a CSV containing these columns:

`strike,call_oi,put_oi,call_ltp,put_ltp`

Example:
```csv
strike,call_oi,put_oi,call_ltp,put_ltp
22400,18000,35000,190,60
22500,42000,31000,138,95
22600,50000,22000,91,145
```

Use the same expiry and a consistent timestamp for all rows. The app does not independently verify the CSV source or freshness.

## Next steps
1. Add timestamp and expiry validation.
2. Add change-in-OI, bid/ask spread and implied-volatility filters.
3. Backtest on historical data with transaction costs and slippage.
4. Connect a licensed market-data provider or broker API only after checking its terms and reliability.
5. Add alerts after testing false positives. Keep auto-order placement disabled by default.
