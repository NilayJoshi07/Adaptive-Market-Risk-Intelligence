# Cell 262
#--------------------------------------------------------
#3Inspect existing VIX-enhanced forecast results
#---------------------------------------------------------

vix_forecast_comparison = validation_vix_forecasts[
    [
        "Actual_Volatility",
        "EGARCH_t",
        "EGARCH_t_VIX_Enhanced",
        "GJR_GARCH_t",
        "GJR_GARCH_t_VIX_Enhanced",
        "GARCH_t",
        "GARCH_t_VIX_Enhanced"
    ]
].copy()

display(vix_forecast_comparison.head(10))

#---------------------------------------------------------------------------
NameError                                 Traceback (most recent call last)
Cell In[420], line 5
      1 # ---------------------------------------------------------
      2 # Inspect existing VIX-enhanced forecast results
      3 # ---------------------------------------------------------
      4 
----> 5 vix_forecast_comparison = validation_vix_forecasts[
      6     [
      7         "Actual_Volatility",
      8         "EGARCH_t",

NameError: name 'validation_vix_forecasts' is not defined


# Cell 263
#---------------------------------------------------------
#Existing EGARCH vs VIX-enhanced EGARCH
#---------------------------------------------------------

for col in [
    "EGARCH_t",
    "EGARCH_t_VIX_Enhanced"
]:

    mae = mean_absolute_error(
        validation_vix_forecasts["Actual_Volatility"],
        validation_vix_forecasts[col]
    )

    rmse = np.sqrt(
        mean_squared_error(
            validation_vix_forecasts["Actual_Volatility"],
            validation_vix_forecasts[col]
        )
    )

    print(f"{col}")
    print(f"MAE :  {mae:.6f}")
    print(f"RMSE: {rmse:.6f}")
    print()

#---------------------------------------------------------------------------
NameError                                 Traceback (most recent call last)
Cell In[629], line 10
      6     "EGARCH_t",
      7     "EGARCH_t_VIX_Enhanced"
      8 ]:
      9 
---> 10     mae = mean_absolute_error(
     11         validation_vix_forecasts["Actual_Volatility"],
     12         validation_vix_forecasts[col]
     13     )

NameError: name 'mean_absolute_error' is not defined

# Cell 271

print("=" * 80)
print("VIX FORECAST CONSTRUCTION AUDIT")
print("=" * 80)

print("\n--- vix_forecast_comparison ---")
print(vix_forecast_comparison.head(10))
print("\nColumns:")
print(vix_forecast_comparison.columns.tolist())

print("\n--- validation_vix_forecasts SAMPLE ---")
print(validation_vix_forecasts.head(10).to_string())

print("\n--- validation_vix_results ---")
print(validation_vix_results.to_string())

print("\n--- validation_vix_accuracy ---")
print(validation_vix_accuracy.to_string())

print("\n--- vix_model fitted sample ---")
print("nobs:", vix_model.nobs)

try:
    print("Model date range:",
          X_vix.index.min(),
          "to",
          X_vix.index.max())
except:
    pass

    ================================================================================
VIX FORECAST CONSTRUCTION AUDIT
================================================================================

--- vix_forecast_comparison ---

# Cell 289

print("validation_forecasts:")
print(validation_forecasts.columns.tolist())

print("\nvalidation_vix_enhanced:")
print(validation_vix_enhanced.columns.tolist())

print("\nvalidation_vix_forecasts:")
print(validation_vix_forecasts.columns.tolist())

# Cell 316
#============================================================
#16.13G — Locate Historical Volatility Model Objects
#============================================================

print("=" * 70)
print("RELEVANT DATAFRAME OBJECTS")
print("=" * 70)

for name, obj in globals().items():
    if hasattr(obj, "shape") and hasattr(obj, "columns"):
        try:
            cols = list(obj.columns)

            relevant = [
                c for c in cols
                if any(term in str(c).lower()
                       for term in [
                           "historical",
                           "ewma",
                           "garch",
                           "gjr",
                           "egarch",
                           "volatility"
                       ])
            ]

            if relevant:
                print(f"\n{name}")
                print(f"Shape: {obj.shape}")
                print(f"Date column: {'Date' in cols}")
                print("Relevant columns:")
                for c in relevant:
                    print(f"   - {c}")

        except Exception:
            pass

======================================================================
RELEVANT DATAFRAME OBJECTS
======================================================================

__
Shape: (3, 3)
Date column: False
Relevant columns:
   - EWMA
   - GARCH
---------------------------------------------------------------------------
RuntimeError                              Traceback (most recent call last)
Cell In[1332], line 9
      5 print("=" * 70)
      6 print("RELEVANT DATAFRAME OBJECTS")
      7 print("=" * 70)
      8 
----> 9 for name, obj in globals().items():
     10     if hasattr(obj, "shape") and hasattr(obj, "columns"):
     11         try:
     12             cols = list(obj.columns)

RuntimeError: dictionary changed size during iteration

# Cell 317
#============================================================
#16.13H — Locate GJR / EGARCH Historical Data
#============================================================

print("=" * 70)
print("DATAFRAMES CONTAINING GJR / EGARCH")
print("=" * 70)

found = 0

for name, obj in globals().items():
    if hasattr(obj, "shape") and hasattr(obj, "columns"):
        try:
            cols = list(obj.columns)

            gjr_cols = [c for c in cols if "gjr" in str(c).lower()]
            egarch_cols = [c for c in cols if "egarch" in str(c).lower()]

            if gjr_cols or egarch_cols:
                found += 1

                print(f"\nOBJECT: {name}")
                print(f"Shape: {obj.shape}")

                print("GJR columns:")
                for c in gjr_cols:
                    print(f"   - {c}")

                print("EGARCH columns:")
                for c in egarch_cols:
                    print(f"   - {c}")

                # Show date information if available
                if "Date" in cols:
                    print(
                        "Date range:",
                        obj["Date"].min(),
                        "to",
                        obj["Date"].max()
                    )
                elif hasattr(obj.index, "min"):
                    print(
                        "Index range:",
                        obj.index.min(),
                        "to",
                        obj.index.max()
                    )

        except Exception:
            pass

print("\n" + "=" * 70)
print("TOTAL MATCHING OBJECTS:", found)
print("=" * 70)

