import os, sys, math, json, traceback
import numpy as np

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from train_model import (
    CURRENCY_PAIRS, MODEL_REGISTRY,
    generate_historical_data, create_features,
    train_single_model, load_model, predict_future,
)
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def _get_model(pair, model_name):
    """Load model — auto-retrain if pkl incompatible (sklearn version mismatch)"""
    try:
        model, scaler, feature_cols = load_model(pair, model_name)
        model.predict(np.zeros((1, len(feature_cols))))
        return model, scaler, feature_cols
    except Exception:
        print(f"  Re-training {model_name} for {pair} due to version mismatch...")
        train_single_model(pair, model_name, days=500, force_train=True)
        return load_model(pair, model_name)


def _evaluate(model, scaler, pair):
    raw_df    = generate_historical_data(pair, days=500)
    feat_df   = create_features(raw_df)
    feat_cols = [c for c in feat_df.columns if c not in ("date", "rate")]
    X         = feat_df[feat_cols].values
    y         = feat_df["rate"].values
    split     = int(len(X) * 0.80)
    X_test_sc = scaler.transform(X[split:])
    y_test    = y[split:]
    y_pred    = model.predict(X_test_sc)
    mae  = float(mean_absolute_error(y_test, y_pred))
    rmse = float(math.sqrt(mean_squared_error(y_test, y_pred)))
    r2   = float(r2_score(y_test, y_pred))
    mape = float(np.mean(np.abs((y_test - y_pred) / (y_test + 1e-10))) * 100)
    acc  = max(0.0, min(100.0, (1 - mae / float(np.mean(y_test))) * 100))
    return {"mae": round(mae,6), "rmse": round(rmse,6),
            "r2": round(r2,4), "mape": round(mape,4), "accuracy": round(acc,2)}


def index(request):
    return render(request, "index.html", {"currency_pairs": list(CURRENCY_PAIRS.keys())})


def get_currencies(request):
    return JsonResponse({"currencies": list(CURRENCY_PAIRS.keys())})


@csrf_exempt
@require_http_methods(["POST"])
def get_historical(request):
    try:
        data = json.loads(request.body)
        df   = generate_historical_data(data.get("pair","USD/EUR"), days=int(data.get("days",90)))
        return JsonResponse({"success": True, "data": df.to_dict(orient="records")})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def predict(request):
    try:
        data       = json.loads(request.body)
        pair       = data.get("pair",            "USD/EUR")
        model_name = data.get("model",           "random_forest")
        pred_days  = int(data.get("prediction_days", 7))

        if pair not in CURRENCY_PAIRS:
            return JsonResponse({"success": False, "error": f"Unknown pair: {pair}"}, status=400)
        if model_name not in MODEL_REGISTRY:
            return JsonResponse({"success": False, "error": f"Unknown model: {model_name}"}, status=400)

        model, scaler, feature_cols = _get_model(pair, model_name)
        hist_df      = generate_historical_data(pair, days=300)
        current_rate = round(float(hist_df["rate"].iloc[-1]), 6)
        predictions  = predict_future(model, scaler, feature_cols, pair, days=pred_days)
        metrics      = _evaluate(model, scaler, pair)

        # Data source — CSV ఉంటే Real, లేకపోతే Synthetic
        import os
        csv_path    = os.path.join(BASE_DIR, "forex_data", f"{pair.replace('/', '_')}.csv")
        data_source = "Yahoo Finance (Real)" if os.path.exists(csv_path) else "Synthetic"

        return JsonResponse({
            "success":     True,
            "pair":        pair,
            "model":       model_name,
            "current_rate": current_rate,
            "metrics":     metrics,
            "historical":  hist_df.tail(60).to_dict(orient="records"),
            "predictions": predictions,
            "data_source": data_source,
            "data_rows":   len(hist_df),
            "from_date":   hist_df["date"].iloc[0],
            "to_date":     hist_df["date"].iloc[-1],
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e),
                             "detail": traceback.format_exc()}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def compare_models(request):
    try:
        data    = json.loads(request.body)
        pair    = data.get("pair", "USD/EUR")
        results = {}
        for model_name in MODEL_REGISTRY:
            try:
                model, scaler, _ = _get_model(pair, model_name)
                results[model_name] = _evaluate(model, scaler, pair)
            except Exception as e:
                results[model_name] = {"error": str(e)}
        return JsonResponse({"success": True, "pair": pair, "comparison": results})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def retrain(request):
    try:
        data       = json.loads(request.body)
        pair       = data.get("pair",  "USD/EUR")
        model_name = data.get("model", "random_forest")
        days       = int(data.get("days", 500))
        metrics    = train_single_model(pair, model_name, days=days, force_train=True)
        return JsonResponse({"success": True, "metrics": metrics})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
