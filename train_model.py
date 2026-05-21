
import os
import sys
import math
import copy
import argparse
import warnings
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import joblib
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

warnings.filterwarnings("ignore")

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR   = os.path.join(BASE_DIR, "forex_data")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DATA_DIR,   exist_ok=True)

CURRENCY_PAIRS = {
    "USD/EUR": {"yahoo": "USDEUR=X", "base": 0.92,    "vol": 0.008},
    "USD/GBP": {"yahoo": "USDGBP=X", "base": 0.79,    "vol": 0.007},
    "USD/JPY": {"yahoo": "USDJPY=X", "base": 149.5,   "vol": 0.90 },
    "USD/INR": {"yahoo": "USDINR=X", "base": 83.10,   "vol": 0.30 },
    "USD/CAD": {"yahoo": "USDCAD=X", "base": 1.36,    "vol": 0.006},
    "USD/AUD": {"yahoo": "USDAUD=X", "base": 1.53,    "vol": 0.009},
    "USD/CHF": {"yahoo": "USDCHF=X", "base": 0.88,    "vol": 0.006},
    "USD/CNY": {"yahoo": "USDCNY=X", "base": 7.24,    "vol": 0.020},
    "USD/SGD": {"yahoo": "USDSGD=X", "base": 1.34,    "vol": 0.005},
    "USD/HKD": {"yahoo": "USDHKD=X", "base": 7.82,    "vol": 0.003},
    "USD/KRW": {"yahoo": "USDKRW=X", "base": 1325.0,  "vol": 5.00 },
    "USD/MXN": {"yahoo": "USDMXN=X", "base": 17.15,   "vol": 0.15 },
    "USD/BRL": {"yahoo": "USDBRL=X", "base": 4.97,    "vol": 0.060},
    "USD/ZAR": {"yahoo": "USDZAR=X", "base": 18.60,   "vol": 0.20 },
    "USD/TRY": {"yahoo": "USDTRY=X", "base": 32.10,   "vol": 0.40 },
    "USD/SAR": {"yahoo": "USDSAR=X", "base": 3.75,    "vol": 0.002},
    "USD/AED": {"yahoo": "USDAED=X", "base": 3.67,    "vol": 0.001},
    "USD/THB": {"yahoo": "USDTHB=X", "base": 35.10,   "vol": 0.20 },
    "USD/MYR": {"yahoo": "USDMYR=X", "base": 4.72,    "vol": 0.030},
    "USD/IDR": {"yahoo": "USDIDR=X", "base": 15750.0, "vol": 60.0 },
    "USD/PHP": {"yahoo": "USDPHP=X", "base": 56.50,   "vol": 0.30 },
    "USD/NZD": {"yahoo": "USDNZD=X", "base": 1.63,    "vol": 0.009},
    "USD/SEK": {"yahoo": "USDSEK=X", "base": 10.42,   "vol": 0.060},
    "USD/NOK": {"yahoo": "USDNOK=X", "base": 10.55,   "vol": 0.070},
    "USD/DKK": {"yahoo": "USDDKK=X", "base": 6.88,    "vol": 0.040},
    "USD/PLN": {"yahoo": "USDPLN=X", "base": 3.98,    "vol": 0.030},
    "USD/ILS": {"yahoo": "USDILS=X", "base": 3.72,    "vol": 0.030},
    "USD/QAR": {"yahoo": "USDQAR=X", "base": 3.64,    "vol": 0.002},
    "USD/KWD": {"yahoo": "USDKWD=X", "base": 0.307,   "vol": 0.001},
    "EUR/GBP": {"yahoo": "EURGBP=X", "base": 0.86,    "vol": 0.005},
    "EUR/JPY": {"yahoo": "EURJPY=X", "base": 162.5,   "vol": 0.80 },
    "EUR/CHF": {"yahoo": "EURCHF=X", "base": 0.96,    "vol": 0.005},
    "EUR/AUD": {"yahoo": "EURAUD=X", "base": 1.66,    "vol": 0.010},
    "EUR/CAD": {"yahoo": "EURCAD=X", "base": 1.48,    "vol": 0.008},
    "EUR/INR": {"yahoo": "EURINR=X", "base": 90.50,   "vol": 0.35 },
    "EUR/CNY": {"yahoo": "EURCNY=X", "base": 7.89,    "vol": 0.025},
    "EUR/SEK": {"yahoo": "EURSEK=X", "base": 11.35,   "vol": 0.060},
    "EUR/NOK": {"yahoo": "EURNOK=X", "base": 11.50,   "vol": 0.070},
    "EUR/PLN": {"yahoo": "EURPLN=X", "base": 4.33,    "vol": 0.030},
    "EUR/TRY": {"yahoo": "EURTRY=X", "base": 34.90,   "vol": 0.45 },
    "GBP/JPY": {"yahoo": "GBPJPY=X", "base": 189.5,   "vol": 1.00 },
    "GBP/CHF": {"yahoo": "GBPCHF=X", "base": 1.12,    "vol": 0.007},
    "GBP/AUD": {"yahoo": "GBPAUD=X", "base": 1.93,    "vol": 0.012},
    "GBP/CAD": {"yahoo": "GBPCAD=X", "base": 1.72,    "vol": 0.009},
    "GBP/INR": {"yahoo": "GBPINR=X", "base": 105.0,   "vol": 0.40 },
    "GBP/NZD": {"yahoo": "GBPNZD=X", "base": 2.05,    "vol": 0.012},
    "GBP/SGD": {"yahoo": "GBPSGD=X", "base": 1.69,    "vol": 0.008},
    "AUD/JPY": {"yahoo": "AUDJPY=X", "base": 97.80,   "vol": 0.60 },
    "AUD/NZD": {"yahoo": "AUDNZD=X", "base": 1.08,    "vol": 0.005},
    "AUD/SGD": {"yahoo": "AUDSGD=X", "base": 0.875,   "vol": 0.005},
    "AUD/INR": {"yahoo": "AUDINR=X", "base": 54.30,   "vol": 0.25 },
    "SGD/JPY": {"yahoo": "SGDJPY=X", "base": 111.5,   "vol": 0.50 },
    "NZD/JPY": {"yahoo": "NZDJPY=X", "base": 91.80,   "vol": 0.55 },
    "NZD/SGD": {"yahoo": "NZDSGD=X", "base": 0.820,   "vol": 0.005},
    "AED/INR": {"yahoo": "AEDINR=X", "base": 22.65,   "vol": 0.080},
    "CHF/JPY": {"yahoo": "CHFJPY=X", "base": 170.0,   "vol": 0.90 },
    "CAD/JPY": {"yahoo": "CADJPY=X", "base": 110.5,   "vol": 0.60 },
}

MODEL_REGISTRY = {
    "linear": LinearRegression(),
    "ridge":  Ridge(alpha=1.0),
    "random_forest": RandomForestRegressor(
        n_estimators=200, max_depth=10,
        min_samples_split=5, random_state=42, n_jobs=-1,
    ),
    "gradient_boost": GradientBoostingRegressor(
        n_estimators=200, max_depth=5,
        learning_rate=0.05, subsample=0.8, random_state=42,
    ),
}


def _load_from_csv(pair, days):
    safe = pair.replace("/", "_")
    path = os.path.join(DATA_DIR, f"{safe}.csv")
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_csv(path)
        if "date" not in df.columns or "rate" not in df.columns:
            return None
        df = df.dropna(subset=["rate"])
        if len(df) < 60:
            return None
        print(f"  📂 CSV loaded : {pair}  ({len(df)} rows)  "
              f"Latest: {df['rate'].iloc[-1]}  ({df['date'].iloc[-1]})")
        return df.tail(days).reset_index(drop=True)
    except Exception as e:
        print(f"  Warning CSV read {pair}: {e}")
        return None


def _download_from_yahoo(pair, days):
    try:
        import yfinance as yf
    except ImportError:
        return None

    symbol = CURRENCY_PAIRS.get(pair, {}).get("yahoo")
    if not symbol:
        return None

    try:
        end_dt   = datetime.now()
        start_dt = end_dt - timedelta(days=days + 60)
        hist = yf.Ticker(symbol).history(
            start=start_dt.strftime("%Y-%m-%d"),
            end=end_dt.strftime("%Y-%m-%d"),
            interval="1d", auto_adjust=True,
        )
        if hist.empty or len(hist) < 30:
            return None

        df = hist[["Close"]].reset_index()
        df.columns = ["date", "rate"]
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None).dt.strftime("%Y-%m-%d")
        df["rate"] = pd.to_numeric(df["rate"], errors="coerce").round(6)
        df = df.dropna().reset_index(drop=True)

        safe = pair.replace("/", "_")
        df.to_csv(os.path.join(DATA_DIR, f"{safe}.csv"), index=False)
        print(f"  ✅ Downloaded  : {pair}  ({len(df)} rows)  "
              f"Latest: {df['rate'].iloc[-1]}  ({df['date'].iloc[-1]})")
        return df.tail(days).reset_index(drop=True)
    except Exception as e:
        print(f"  Yahoo failed  : {pair} — {e}")
        return None


def _synthetic_fallback(pair, days):
    print(f"  🔁 Synthetic   : {pair}")
    info = CURRENCY_PAIRS.get(pair, {"base": 1.0, "vol": 0.01})
    base, vol = info["base"], info["vol"]
    np.random.seed(42 + abs(hash(pair)) % 1000)
    dates  = [datetime.now() - timedelta(days=days - i) for i in range(days)]
    prices = [base]
    for _ in range(1, days):
        prev = prices[-1]
        prices.append(round(max(prev + 0.05*(base-prev) + vol*np.random.randn(), base*0.5), 6))
    return pd.DataFrame({
        "date": [d.strftime("%Y-%m-%d") for d in dates],
        "rate": prices,
    })


def generate_historical_data(pair: str, days: int = 730) -> pd.DataFrame:
    """Priority: CSV cache → Yahoo live → Synthetic fallback"""
    df = _load_from_csv(pair, days)
    if df is not None:
        return df
    df = _download_from_yahoo(pair, days)
    if df is not None:
        return df
    return _synthetic_fallback(pair, days)


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
    df = df.dropna(subset=["rate"]).reset_index(drop=True)

    for lag in [1, 2, 3, 5, 7, 10, 14, 21, 30]:
        df[f"lag_{lag}"] = df["rate"].shift(lag)
    for w in [7, 14, 30]:
        df[f"roll_mean_{w}"] = df["rate"].rolling(w).mean()
        df[f"roll_std_{w}"]  = df["rate"].rolling(w).std()
        df[f"roll_min_{w}"]  = df["rate"].rolling(w).min()
        df[f"roll_max_{w}"]  = df["rate"].rolling(w).max()

    df["ema_7"]       = df["rate"].ewm(span=7,  adjust=False).mean()
    df["ema_14"]      = df["rate"].ewm(span=14, adjust=False).mean()
    df["ema_30"]      = df["rate"].ewm(span=30, adjust=False).mean()
    df["momentum_7"]  = df["rate"] - df["rate"].shift(7)
    df["momentum_30"] = df["rate"] - df["rate"].shift(30)
    df["roc_7"]       = df["rate"].pct_change(7)  * 100
    df["roc_14"]      = df["rate"].pct_change(14) * 100

    rm20 = df["rate"].rolling(20).mean()
    rs20 = df["rate"].rolling(20).std()
    df["bb_upper"] = rm20 + 2 * rs20
    df["bb_lower"] = rm20 - 2 * rs20
    df["bb_pos"]   = (df["rate"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"] + 1e-10)

    dt = pd.to_datetime(df["date"])
    df["day_of_week"] = dt.dt.dayofweek
    df["month"]       = dt.dt.month
    df["quarter"]     = dt.dt.quarter
    df["day_of_year"] = dt.dt.dayofyear

    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def train_single_model(pair: str, model_name: str, days: int = 730, cv_folds: int = 5) -> dict:

    print(f"\nTraining [{model_name}] on {pair} ...")

    raw_df = generate_historical_data(pair, days=days)

    csv_exists = os.path.exists(
        os.path.join(DATA_DIR, f"{pair.replace('/','_')}.csv")
    )

    data_source = "REAL" if csv_exists else "SYNTHETIC"

    df = create_features(raw_df)

    FEATURE_COLS = [c for c in df.columns if c not in ("date", "rate")]

    X = df[FEATURE_COLS].values
    y = df["rate"].values

    split = int(len(X) * 0.80)

    X_tr, X_te = X[:split], X[split:]
    y_tr, y_te = y[:split], y[split:]

    scaler = MinMaxScaler()

    X_tr_sc = scaler.fit_transform(X_tr)
    X_te_sc = scaler.transform(X_te)

    model = copy.deepcopy(MODEL_REGISTRY[model_name])

    model.fit(X_tr_sc, y_tr)

    y_pred = model.predict(X_te_sc)

    mae = float(mean_absolute_error(y_te, y_pred))
    rmse = float(math.sqrt(mean_squared_error(y_te, y_pred)))
    r2 = float(r2_score(y_te, y_pred))

    mape = float(
        np.mean(np.abs((y_te - y_pred) / (y_te + 1e-10))) * 100
    )

    acc = float(
        max(0.0, min(100.0, (1 - mae / np.mean(y_te)) * 100))
    )

    tscv = TimeSeriesSplit(n_splits=cv_folds)

    cv_scores = cross_val_score(
        copy.deepcopy(model),
        scaler.transform(X),
        y,
        cv=tscv,
        scoring="neg_mean_absolute_error"
    )

    metrics = {
        "pair": pair,
        "model": model_name,
        "data_source": data_source,
        "mae": round(mae, 6),
        "rmse": round(rmse, 6),
        "r2": round(r2, 4),
        "mape": round(mape, 4),
        "accuracy": round(acc, 2),
        "cv_mae": round(float(-cv_scores.mean()), 6),
    }

    safe = pair.replace("/", "_")

    joblib.dump(
        model,
        os.path.join(MODELS_DIR, f"{safe}_{model_name}_model.pkl")
    )

    joblib.dump(
        scaler,
        os.path.join(MODELS_DIR, f"{safe}_{model_name}_scaler.pkl")
    )

    joblib.dump(
        FEATURE_COLS,
        os.path.join(MODELS_DIR, f"{safe}_{model_name}_features.pkl")
    )

    return metrics


def load_model(pair: str, model_name: str):

    safe = pair.replace("/", "_")

    return (
        joblib.load(os.path.join(MODELS_DIR, f"{safe}_{model_name}_model.pkl")),
        joblib.load(os.path.join(MODELS_DIR, f"{safe}_{model_name}_scaler.pkl")),
        joblib.load(os.path.join(MODELS_DIR, f"{safe}_{model_name}_features.pkl")),
    )


def predict_future(model, scaler, feature_cols, pair, days=7, history_days=730):

    df_work = generate_historical_data(pair, days=history_days)

    predictions = []

    for _ in range(days):

        df_feat = create_features(df_work)

        if df_feat.empty:
            break

        last_sc = scaler.transform(
            df_feat[feature_cols].iloc[-1:].values
        )

        pred = round(float(model.predict(last_sc)[0]), 6)

        next_dt = (
            datetime.strptime(df_work["date"].iloc[-1], "%Y-%m-%d")
            + timedelta(days=1)
        ).strftime("%Y-%m-%d")

        predictions.append({
            "date": next_dt,
            "predicted_rate": pred
        })

        df_work = pd.concat(
            [
                df_work,
                pd.DataFrame({
                    "date": [next_dt],
                    "rate": [pred]
                })
            ],
            ignore_index=True
        )

    return predictions


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--pair", type=str, default=None)

    parser.add_argument(
        "--model",
        type=str,
        default=None,
        choices=list(MODEL_REGISTRY.keys())
    )

    parser.add_argument("--days", type=int, default=730)

    parser.add_argument("--all", action="store_true")

    args = parser.parse_args()

    pairs = (
        list(CURRENCY_PAIRS.keys())
        if (args.all or not args.pair)
        else [args.pair]
    )

    models = (
        list(MODEL_REGISTRY.keys())
        if (args.all or not args.model)
        else [args.model]
    )

    for pair in pairs:
        for model_name in models:

            try:
                metrics = train_single_model(
                    pair,
                    model_name,
                    days=args.days
                )

                print(metrics)

            except Exception as exc:
                print(f"ERROR: {pair}/{model_name}: {exc}")


if __name__ == "__main__":
    main()
