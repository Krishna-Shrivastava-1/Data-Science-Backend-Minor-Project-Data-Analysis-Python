from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pandas as pd
import io
import json
import numpy as np
# Flask Server Instance
app = Flask(__name__)
# / Route
@app.route('/')
def home():
    return jsonify({"message": "DataMind API running"}), 200

# @app.route("/analyze", methods=["POST"])
# def analyze_data():
#     try:
#         data = request.get_json()
#         print("📥 Raw data received:", data)
#         print("📦 Type of data:", type(data))

#         # Safety check
#         if not isinstance(data, list):
#             return jsonify({"error": "Data must be a list of records"}), 400

#         df = pd.DataFrame(data)
#         print("✅ DataFrame created")

#         # --- Smart dtype inference ---
#         for col in df.columns:
#             series = df[col]
#             # Try datetime first
#             converted_date = pd.to_datetime(series, errors='coerce')
#             if converted_date.notna().sum() > len(series) * 0.8:
#                 df[col] = converted_date
#                 continue
#             # Then numeric
#             converted_num = pd.to_numeric(series, errors='coerce')
#             if converted_num.notna().sum() > len(series) * 0.8:
#                 df[col] = converted_num
#                 continue
#             # Otherwise string
#             df[col] = series.astype("string")

#         df = df.convert_dtypes()  # ensures best possible dtype

#         # Prepare dtypes dict
#         dtypes = df.dtypes.apply(str).to_dict()

#         # Prepare summary
#         summary = {
#             "rows": len(df),
#             "columns": len(df.columns),
#             "missing_values": int(df.isna().sum().sum()),
#             "duplicate_rows": int(df.duplicated().sum())
#         }

#         # Return **full dataset** as `cleaned_data` to match `/clean`
#         cleaned_data = df.to_dict(orient="records")

#         return jsonify({
#             "summary": summary,
#             "dtypes": dtypes,
#             "cleaned_data": cleaned_data
#         }), 200

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return jsonify({"error": str(e)}), 500



# @app.route("/clean", methods=["POST"])
# def clean_data():
#     try:
#         data = request.get_json()
#         df = pd.DataFrame(data)
#         # print(df.columns)
#         # Basic cleaning
#         before_rows = len(df)
#         df = df.drop_duplicates().dropna()
#         after_rows = len(df)
#         removed_rows = before_rows - after_rows

#         summary = {
#             "rows_before": before_rows,
#             "rows_after": after_rows,
#             "removed_rows": removed_rows,
#             "columns": len(df.columns)
#         }

#         cleaned_data = df.to_dict(orient="records")  # 👈 full dataset

#         return jsonify({
#             "summary": summary,
#             "cleaned_data": cleaned_data  # 👈 send full cleaned dataset
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

def safe_jsonify(data):
    """Convert NaN/NaT to None for valid JSON."""
    # Replace NaN/NaT with None before dumping
    safe_data = json.loads(json.dumps(data, default=str))
    return Response(json.dumps(safe_data, allow_nan=False), mimetype="application/json")


@app.route("/analyze", methods=["POST"])
@app.route("/analyze", methods=["POST"])
def analyze_data():
    try:
        data = request.get_json()
        print("📥 Raw data received:", type(data))

        if not isinstance(data, list):
            return jsonify({"error": "Data must be a list of records"}), 400

        df = pd.DataFrame(data)
        print("✅ DataFrame created with", len(df), "rows")

        # Normalize null-like values
        null_like = ["null", "None", "NaN", "nan", "", "undefined", "Null", "NONE"]
        df = df.replace(null_like, np.nan)

        # Smart dtype inference
        for col in df.columns:
            series = df[col]

            # Try datetime (if mostly valid)
            converted_date = pd.to_datetime(series, errors="coerce")
            if converted_date.notna().sum() > len(series) * 0.8:
                df[col] = converted_date
                continue

            # Try numeric (if mostly valid)
            converted_num = pd.to_numeric(series, errors="coerce")
            if converted_num.notna().sum() > len(series) * 0.8:
                df[col] = converted_num
                continue

            # Fallback: string
            df[col] = series.astype("string")

        df = df.convert_dtypes()

        # --- Basic summary ---
        summary = {
            "rows": len(df),
            "columns": len(df.columns),
            "missing_values": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
        }

        # --- Data type info ---
        dtypes = df.dtypes.apply(str).to_dict()

        # --- Statistical summary (for numeric columns only) ---
        numeric_df = df.select_dtypes(include=["number"])
        stats = {}

        if not numeric_df.empty:
            stats = {
                col: {
                    "mean": float(numeric_df[col].mean(skipna=True)),
                    "median": float(numeric_df[col].median(skipna=True)),
                    "mode": (
                        numeric_df[col].mode(dropna=True).tolist()[0]
                        if not numeric_df[col].mode(dropna=True).empty
                        else None
                    ),
                    "std_dev": float(numeric_df[col].std(skipna=True)),
                    "min": float(numeric_df[col].min(skipna=True)),
                    "max": float(numeric_df[col].max(skipna=True)),
                    "count": int(numeric_df[col].count()),
                }
                for col in numeric_df.columns
            }

        # --- Pandas describe (for numeric columns) ---
        describe_df = numeric_df.describe(include="all").transpose()
        describe_dict = describe_df.to_dict(orient="index")

        cleaned_data = df.where(pd.notnull(df), None).to_dict(orient="records")

        return safe_jsonify({
            "message": "Raw data summary with detailed statistics",
            "summary": summary,
            "dtypes": dtypes,
            "numeric_stats": stats,
            "describe": describe_dict,
            "cleaned_data": cleaned_data
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/clean", methods=["POST"])
def clean_data():
    try:
        data = request.get_json()

        if not isinstance(data, list):
            return jsonify({"error": "Data must be a list of records"}), 400

        df = pd.DataFrame(data)

        # Normalize null-like values
        null_like = ["null", "None", "NaN", "nan", "", "undefined", "Null", "NONE"]
        df = df.replace(null_like, np.nan)

        before_rows = len(df)

        # Remove duplicates
        df = df.drop_duplicates()

        # ❌ Drop any row that contains even one NaN value
        df = df.dropna(how="any")

        after_rows = len(df)
        removed_rows = before_rows - after_rows

        summary = {
            "rows_before": before_rows,
            "rows_after": after_rows,
            "removed_rows": removed_rows,
            "columns": len(df.columns)
        }

        describe_data = {}
        numeric_stats = {}

        # ---- Stats generation (only if data remains) ----
        if not df.empty:
            numeric_cols = df.select_dtypes(include=[np.number]).columns

            if len(numeric_cols) > 0:
                describe_data = df[numeric_cols].describe().to_dict()

                for col in numeric_cols:
                    series = df[col].dropna()
                    if not series.empty:
                        numeric_stats[col] = {
                            "count": int(series.count()),
                            "mean": float(series.mean()),
                            "median": float(series.median()),
                            "mode": float(series.mode().iloc[0]) if not series.mode().empty else None,
                            "std_dev": float(series.std()) if series.count() > 1 else 0,
                            "min": float(series.min()),
                            "max": float(series.max()),
                        }

        cleaned_data = df.where(pd.notnull(df), None).to_dict(orient="records")

        return safe_jsonify({
            "message": "Cleaned dataset summary with detailed statistics",
            "summary": summary,
            "describe": describe_data,
            "numeric_stats": numeric_stats,
            "cleaned_data": cleaned_data
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
