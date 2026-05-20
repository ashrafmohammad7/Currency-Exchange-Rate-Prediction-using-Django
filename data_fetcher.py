
import os
import time
import argparse
import warnings
import pandas as pd
from datetime import datetime, timedelta

warnings.filterwarnings("ignore")

# ── Data save folder ──────────────────────────────────────────────────
DATA_DIR = "forex_data"
os.makedirs(DATA_DIR, exist_ok=True)

YAHOO_SYMBOLS = {
    # USD Base Pairs
    "USD/EUR": "USDEUR=X",
    "USD/GBP": "USDGBP=X",
    "USD/JPY": "USDJPY=X",
    "USD/INR": "USDINR=X",
    "USD/CAD": "USDCAD=X",
    "USD/AUD": "USDAUD=X",
    "USD/CHF": "USDCHF=X",
    "USD/CNY": "USDCNY=X",
    "USD/SGD": "USDSGD=X",
    "USD/HKD": "USDHKD=X",
    "USD/KRW": "USDKRW=X",
    "USD/MXN": "USDMXN=X",
    "USD/BRL": "USDBRL=X",
    "USD/ZAR": "USDZAR=X",
    "USD/TRY": "USDTRY=X",
    "USD/SAR": "USDSAR=X",
    "USD/AED": "USDAED=X",
    "USD/THB": "USDTHB=X",
    "USD/MYR": "USDMYR=X",
    "USD/IDR": "USDIDR=X",
    "USD/PHP": "USDPHP=X",
    "USD/NZD": "USDNZD=X",
    "USD/SEK": "USDSEK=X",
    "USD/NOK": "USDNOK=X",
    "USD/DKK": "USDDKK=X",
    "USD/PLN": "USDPLN=X",
    "USD/ILS": "USDILS=X",
    "USD/QAR": "USDQAR=X",
    "USD/KWD": "USDKWD=X",

    # EUR Cross Pairs
    "EUR/GBP": "EURGBP=X",
    "EUR/JPY": "EURJPY=X",
    "EUR/CHF": "EURCHF=X",
    "EUR/AUD": "EURAUD=X",
    "EUR/CAD": "EURCAD=X",
    "EUR/INR": "EURINR=X",
    "EUR/CNY": "EURCNY=X",
    "EUR/SEK": "EURSEK=X",
    "EUR/NOK": "EURNOK=X",
    "EUR/PLN": "EURPLN=X",
    "EUR/TRY": "EURTRY=X",

    # GBP Cross Pairs
    "GBP/JPY": "GBPJPY=X",
    "GBP/CHF": "GBPCHF=X",
    "GBP/AUD": "GBPAUD=X",
    "GBP/CAD": "GBPCAD=X",
    "GBP/INR": "GBPINR=X",
    "GBP/NZD": "GBPNZD=X",
    "GBP/SGD": "GBPSGD=X",

    # Asian Cross Pairs
    "AUD/JPY": "AUDJPY=X",
    "AUD/NZD": "AUDNZD=X",
    "AUD/SGD": "AUDSGD=X",
    "AUD/INR": "AUDINR=X",
    "SGD/JPY": "SGDJPY=X",
    "NZD/JPY": "NZDJPY=X",
    "NZD/SGD": "NZDSGD=X",

    # Middle East
    "AED/INR": "AEDINR=X",

    # CHF / CAD Pairs
    "CHF/JPY": "CHFJPY=X",
    "CAD/JPY": "CADJPY=X",
}


# ──  ────────────
FALLBACK_RATES = {
    "USD/EUR": 0.92,   "USD/GBP": 0.79,   "USD/JPY": 149.5,
    "USD/INR": 83.10,  "USD/CAD": 1.36,   "USD/AUD": 1.53,
    "USD/CHF": 0.88,   "USD/CNY": 7.24,   "USD/SGD": 1.34,
    "USD/HKD": 7.82,   "USD/KRW": 1325.0, "USD/MXN": 17.15,
    "USD/BRL": 4.97,   "USD/ZAR": 18.60,  "USD/TRY": 32.10,
    "USD/SAR": 3.75,   "USD/AED": 3.67,   "USD/THB": 35.10,
    "USD/MYR": 4.72,   "USD/IDR": 15750., "USD/PHP": 56.50,
    "USD/NZD": 1.63,   "USD/SEK": 10.42,  "USD/NOK": 10.55,
    "USD/DKK": 6.88,   "USD/PLN": 3.98,   "USD/ILS": 3.72,
    "USD/QAR": 3.64,   "USD/KWD": 0.307,
    "EUR/GBP": 0.86,   "EUR/JPY": 162.5,  "EUR/CHF": 0.96,
    "EUR/AUD": 1.66,   "EUR/CAD": 1.48,   "EUR/INR": 90.5,
    "EUR/CNY": 7.89,   "EUR/SEK": 11.35,  "EUR/NOK": 11.50,
    "EUR/PLN": 4.33,   "EUR/TRY": 34.90,
    "GBP/JPY": 189.5,  "GBP/CHF": 1.12,   "GBP/AUD": 1.93,
    "GBP/CAD": 1.72,   "GBP/INR": 105.0,  "GBP/NZD": 2.05,
    "GBP/SGD": 1.69,
    "AUD/JPY": 97.80,  "AUD/NZD": 1.08,   "AUD/SGD": 0.875,
    "AUD/INR": 54.30,  "SGD/JPY": 111.5,  "NZD/JPY": 91.80,
    "NZD/SGD": 0.820,  "AED/INR": 22.65,
    "CHF/JPY": 170.0,  "CAD/JPY": 110.5,
}


def _cache_path(pair: str) -> str:
    """CSV file path for caching downloaded data."""
    safe = pair.replace("/", "_")
    return os.path.join(DATA_DIR, f"{safe}.csv")


def _is_cache_fresh(pair: str, max_age_hours: int = 12) -> bool:
    
    path = _cache_path(pair)
    if not os.path.exists(path):
        return False
    age = time.time() - os.path.getmtime(path)
    return age < max_age_hours * 3600


def download_pair(pair: str, days: int = 730) -> pd.DataFrame | None:

    try:
        import yfinance as yf
    except ImportError:
        print("  ❌ yfinance not installed. Run: pip install yfinance")
        return None

    symbol = YAHOO_SYMBOLS.get(pair)
    if not symbol:
        print(f"  ⚠  No Yahoo symbol found for {pair}")
        return None

    try:
        end_date   = datetime.now()
        start_date = end_date - timedelta(days=days + 30)  # extra buffer

        ticker = yf.Ticker(symbol)
        hist   = ticker.history(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval="1d",
            auto_adjust=True,
        )

        if hist.empty or len(hist) < 30:
            print(f"  ⚠  Insufficient data for {pair} ({len(hist)} rows)")
            return None

        df = hist[["Close"]].copy()
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df = df.reset_index()
        df.columns = ["date", "rate"]
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        df["rate"] = df["rate"].round(6)
        df = df.dropna().reset_index(drop=True)

        print(f"  ✅ {pair}: {len(df)} rows  "
              f"({df['date'].iloc[0]} → {df['date'].iloc[-1]})  "
              f"Latest rate: {df['rate'].iloc[-1]}")
        return df

    except Exception as e:
        print(f"  ❌ Failed to download {pair}: {e}")
        return None


def fetch_and_cache(pair: str, days: int = 730, force: bool = False) -> pd.DataFrame | None:
    
    cache = _cache_path(pair)


    if not force and _is_cache_fresh(pair):
        try:
            df = pd.read_csv(cache)
            return df.tail(days).reset_index(drop=True)
        except Exception:
            pass

    
    df = download_pair(pair, days=days)

    if df is not None and len(df) >= 30:
        df.to_csv(cache, index=False)
        return df.tail(days).reset_index(drop=True)

    if os.path.exists(cache):
        print(f"  📂 Using cached data for {pair}")
        try:
            df = pd.read_csv(cache)
            return df.tail(days).reset_index(drop=True)
        except Exception:
            pass

    return None


def load_data(pair: str, days: int = 730) -> pd.DataFrame | None:
    
    return fetch_and_cache(pair, days=days)


def download_all(pairs: list = None, days: int = 730, force: bool = False):
    
    if pairs is None:
        pairs = list(YAHOO_SYMBOLS.keys())

    print(f"\n{'═'*60}")
    print(f"  ForexML — Real Data Downloader")
    print(f"  Pairs: {len(pairs)}   Days: {days}")
    print(f"{'═'*60}\n")

    success, failed = [], []

    for i, pair in enumerate(pairs, 1):
        print(f"[{i:02d}/{len(pairs)}] Downloading {pair} ...", end=" ")
        df = fetch_and_cache(pair, days=days, force=force)
        if df is not None and len(df) >= 30:
            success.append(pair)
        else:
            failed.append(pair)
            print(f"  ⚠  FAILED — will use synthetic fallback")
        time.sleep(0.3)  

    print(f"\n{'═'*60}")
    print(f"  ✅ Success : {len(success)}/{len(pairs)} pairs")
    if failed:
        print(f"  ⚠  Failed  : {len(failed)} pairs → synthetic fallback")
        for p in failed:
            print(f"       - {p}")
    print(f"  📁 Data saved to: ./{DATA_DIR}/")
    print(f"{'═'*60}")
    print(f"\n  ▶  Now run: python train_model.py\n")

    return success, failed


def show_summary():
    
    print(f"\n{'─'*55}")
    print(f"  Downloaded Data Summary")
    print(f"{'─'*55}")
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    if not files:
        print("  No data downloaded yet. Run: python data_fetcher.py")
        return
    total_rows = 0
    for f in sorted(files):
        pair = f.replace("_", "/").replace(".csv", "")
        path = os.path.join(DATA_DIR, f)
        try:
            df = pd.read_csv(path)
            rows = len(df)
            total_rows += rows
            latest = df["rate"].iloc[-1] if "rate" in df.columns else "?"
            date   = df["date"].iloc[-1]  if "date" in df.columns else "?"
            print(f"  {pair:<12} {rows:>4} rows   latest: {latest:<12} ({date})")
        except Exception:
            print(f"  {pair:<12} [corrupted]")
    print(f"{'─'*55}")
    print(f"  Total: {len(files)} pairs, {total_rows:,} rows")
    print(f"{'─'*55}\n")


# ── CLI ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ForexML Real Data Downloader")
    parser.add_argument("--pair",    type=str,  help="Single pair e.g. USD/INR")
    parser.add_argument("--days",    type=int,  default=730, help="Days of history (default 730)")
    parser.add_argument("--force",   action="store_true",   help="Force re-download (ignore cache)")
    parser.add_argument("--summary", action="store_true",   help="Show downloaded data summary")
    args = parser.parse_args()

    if args.summary:
        show_summary()
    elif args.pair:
        print(f"\nDownloading {args.pair} ...")
        df = fetch_and_cache(args.pair, days=args.days, force=args.force)
        if df is not None:
            print(f"Downloaded {len(df)} rows")
            print(df.tail(5).to_string(index=False))
        else:
            print("Download failed — check internet connection")
    else:
        download_all(days=args.days, force=args.force)
