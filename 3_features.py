"""
NHANES PROJECT - STEP 3 (FIXED)
Feature Engineering & Preparation for ML
- Fixed: ChainedAssignmentError (pandas Copy-on-Write)
- Fixed: Missing values not fully imputed
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# ── YOUR MYSQL DETAILS ───────────────────────────────────────────────────────
MYSQL_HOST     = "127.0.0.1"
MYSQL_PORT     = 3306
MYSQL_USER     = "root"
MYSQL_PASSWORD = quote_plus("VIS@srm3")
MYSQL_DATABASE = "nhanes_project"
# ─────────────────────────────────────────────────────────────────────────────

def create_db_engine():
    url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    return create_engine(url)


def load_data():
    print("=" * 70)
    print("  STEP 3: FEATURE ENGINEERING (FIXED)")
    print("=" * 70)
    print("\n[1/7] Loading data from MySQL...")

    engine = create_db_engine()
    df = pd.read_sql("SELECT * FROM nhanes_cleaned", engine)
    df = df.copy()  # ensure we own this dataframe

    print(f"  ✓ Loaded {len(df):,} rows, {len(df.columns)} columns")
    print(f"  ✓ Missing values before cleaning: {df.isna().sum().sum():,}")
    return df


def handle_missing_values(df):
    """Impute ALL missing values properly using pandas recommended syntax."""
    print("\n[2/7] Handling missing values...")

    df = df.copy()

    # ── NUMERIC: fill with MEDIAN ──────────────────────────────────────────
    median_cols = [
        'systolic_bp', 'diastolic_bp',
        'hba1c', 'fasting_glucose', 'fasting_insulin',
        'total_cholesterol', 'hdl_cholesterol',
        'triglycerides', 'ldl_cholesterol',
        'c_reactive_protein',
        'weight_kg', 'height_cm', 'bmi', 'waist_cm',
        'sleep_hours_weekday', 'sleep_hours_weekend',
        'income_poverty_ratio'
    ]

    for col in median_cols:
        if col in df.columns and df[col].isna().sum() > 0:
            median_val = df[col].median()
            before = df[col].isna().sum()
            df = df.assign(**{col: df[col].fillna(median_val)})
            print(f"  {col:<35} {before:>5} nulls → median {median_val:.1f}")

    # ── LIFESTYLE: fill with 0 (no activity/smoking/drinking = 0) ──────────
    zero_cols = [
        'moderate_activity_min', 'vigorous_activity_min',
        'alcohol_drinks_per_week', 'cigarettes_per_day',
        'fast_food_times_per_week', 'depression_score',
        'total_activity_min'
    ]

    for col in zero_cols:
        if col in df.columns and df[col].isna().sum() > 0:
            before = df[col].isna().sum()
            df = df.assign(**{col: df[col].fillna(0)})
            print(f"  {col:<35} {before:>5} nulls → 0")

    # ── BINARY DISEASE LABELS: fill with 0 (assume healthy if not asked) ───
    binary_cols = [
        'diabetes_diagnosed', 'cvd_history',
        'hypertension_diagnosed', 'on_bp_medication',
        'smoking_status'
    ]

    for col in binary_cols:
        if col in df.columns and df[col].isna().sum() > 0:
            before = df[col].isna().sum()
            df = df.assign(**{col: df[col].fillna(0)})
            print(f"  {col:<35} {before:>5} nulls → 0")

    # ── CATEGORICAL: fill with MODE ─────────────────────────────────────────
    mode_cols = ['education', 'marital_status', 'race', 'gender']

    for col in mode_cols:
        if col in df.columns and df[col].isna().sum() > 0:
            mode_val = df[col].mode()[0]
            before = df[col].isna().sum()
            df = df.assign(**{col: df[col].fillna(mode_val)})
            print(f"  {col:<35} {before:>5} nulls → mode {mode_val}")

    # ── TARGET STAGE COLUMNS: fill with 0 ──────────────────────────────────
    stage_cols = ['diabetes_stage', 'hypertension_stage', 'metabolic_syndrome']
    for col in stage_cols:
        if col in df.columns and df[col].isna().sum() > 0:
            before = df[col].isna().sum()
            df = df.assign(**{col: df[col].fillna(0)})
            print(f"  {col:<35} {before:>5} nulls → 0")

    # ── DEPRESSION CATEGORY: fill with 'None' ──────────────────────────────
    if 'depression_category' in df.columns:
        df = df.assign(depression_category=df['depression_category'].fillna('None'))

    remaining = df.isna().sum().sum()
    print(f"\n  ✓ Missing values remaining: {remaining}")
    if remaining > 0:
        still_null = df.isna().sum()
        still_null = still_null[still_null > 0]
        print(f"  Still null:")
        for col, cnt in still_null.items():
            print(f"    {col}: {cnt}")
    return df


def create_engineered_features(df):
    """Create new features."""
    print("\n[3/7] Creating engineered features...")

    df = df.copy()

    # BMI category
    df = df.assign(bmi_category=pd.cut(
        df['bmi'],
        bins=[0, 18.5, 25, 30, 100],
        labels=['Underweight', 'Normal', 'Overweight', 'Obese']
    ))
    print("  ✓ bmi_category")

    # Age group
    df = df.assign(age_group=pd.cut(
        df['age'],
        bins=[0, 35, 50, 65, 100],
        labels=['18-34', '35-49', '50-64', '65+']
    ))
    print("  ✓ age_group")

    # Cholesterol ratios
    df = df.assign(
        total_hdl_ratio = df['total_cholesterol'] / df['hdl_cholesterol'].replace(0, np.nan),
        ldl_hdl_ratio   = df['ldl_cholesterol'] / df['hdl_cholesterol'].replace(0, np.nan)
    )
    # Fill any NaN from division
    df = df.assign(
        total_hdl_ratio = df['total_hdl_ratio'].fillna(df['total_hdl_ratio'].median()),
        ldl_hdl_ratio   = df['ldl_hdl_ratio'].fillna(df['ldl_hdl_ratio'].median())
    )
    print("  ✓ total_hdl_ratio, ldl_hdl_ratio")

    # Pulse pressure
    df = df.assign(pulse_pressure=df['systolic_bp'] - df['diastolic_bp'])
    print("  ✓ pulse_pressure")

    # HOMA-IR (insulin resistance)
    df = df.assign(homa_ir=(df['fasting_glucose'] * df['fasting_insulin']) / 405)
    print("  ✓ homa_ir")

    # Activity level
    df = df.assign(activity_level=pd.cut(
        df['total_activity_min'],
        bins=[-1, 0, 150, 300, 99999],
        labels=['Sedentary', 'Low', 'Moderate', 'High']
    ))
    print("  ✓ activity_level")

    # Waist-to-height ratio
    df = df.assign(waist_height_ratio=df['waist_cm'] / df['height_cm'])
    print("  ✓ waist_height_ratio")

    # Average sleep
    df = df.assign(
        avg_sleep_hours=(df['sleep_hours_weekday'] * 5 + df['sleep_hours_weekend'] * 2) / 7
    )
    print("  ✓ avg_sleep_hours")

    # Fill NaN in new features
    for col in ['total_hdl_ratio', 'ldl_hdl_ratio', 'pulse_pressure',
                'homa_ir', 'waist_height_ratio', 'avg_sleep_hours']:
        if df[col].isna().sum() > 0:
            df = df.assign(**{col: df[col].fillna(df[col].median())})

    print(f"\n  ✓ Features created. Missing after engineering: {df.isna().sum().sum()}")
    return df


def encode_categoricals(df):
    """One-hot encode all categorical variables."""
    print("\n[4/7] Encoding categorical variables...")

    df = df.copy()

    # Fill NaN in categoricals before encoding
    cat_cols = ['bmi_category', 'age_group', 'activity_level',
                'smoking_status', 'depression_category',
                'gender', 'race', 'education', 'marital_status']

    for col in cat_cols:
        if col in df.columns:
            if df[col].dtype.name == 'category':
                df[col] = df[col].cat.add_categories('Unknown')
            df = df.assign(**{col: df[col].fillna('Unknown')})

    # One-hot encode
    for col in cat_cols:
        if col in df.columns:
            dummies = pd.get_dummies(df[col], prefix=col, drop_first=True, dtype=int)
            df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
            print(f"  ✓ {col:<30} → {len(dummies.columns)} dummy columns")

    print(f"\n  ✓ Encoding done. Missing after encoding: {df.isna().sum().sum()}")
    return df


def prepare_datasets(df):
    """Split into X (features) and y (targets)."""
    print("\n[5/7] Preparing datasets...")

    df = df.copy()

    target_cols = [
        'diabetes_diagnosed', 'cvd_history', 'hypertension_diagnosed',
        'diabetes_stage', 'hypertension_stage', 'metabolic_syndrome',
        'obesity_stage'
    ]

    exclude_cols = ['SEQN', 'depression_category'] + target_cols

    feature_cols = [c for c in df.columns if c not in exclude_cols]

    X = df[feature_cols].copy()
    y = df[['SEQN'] + target_cols].copy()

    # Final check — fill any remaining NaN in X
    for col in X.columns:
        if X[col].isna().sum() > 0:
            if X[col].dtype in [np.float64, np.int64]:
                X = X.assign(**{col: X[col].fillna(X[col].median())})
            else:
                X = X.assign(**{col: X[col].fillna(0)})

    print(f"  Features (X): {X.shape[1]} columns")
    print(f"  Targets  (y): {len(target_cols)} tasks")
    print(f"  Rows:         {len(X):,}")
    print(f"  Missing in X: {X.isna().sum().sum()}")
    print(f"  Missing in y: {y.isna().sum().sum()}")

    return X, y, df


def save_files(X, y, df):
    """Save all datasets."""
    print("\n[6/7] Saving files...")

    import os
    os.makedirs('data', exist_ok=True)

    X.to_csv('data/X_features.csv', index=False)
    y.to_csv('data/y_targets.csv', index=False)
    df.to_csv('data/nhanes_final.csv', index=False)

    print(f"  ✓ data/X_features.csv  ({X.shape[0]:,} rows, {X.shape[1]} cols)")
    print(f"  ✓ data/y_targets.csv   ({y.shape[0]:,} rows, {y.shape[1]} cols)")
    print(f"  ✓ data/nhanes_final.csv (full dataset)")


def print_summary(X, y):
    print("\n[7/7] Final Summary")
    print("=" * 70)

    print(f"\n  Total samples:     {len(X):,}")
    print(f"  Total features:    {X.shape[1]}")
    print(f"  Missing in X:      {X.isna().sum().sum()}  ← should be 0")

    print(f"\n  Target distributions:")
    for col in y.columns:
        if col == 'SEQN':
            continue
        vc = y[col].value_counts().sort_index().to_dict()
        print(f"    {col:<35} {vc}")

    print("\n" + "=" * 70)
    print("  ✅ STEP 3 COMPLETE — READY FOR STEP 4: MODEL TRAINING")
    print("=" * 70)
    print("\n  Run: python 4_train_models.py\n")


def main():
    df = load_data()
    df = handle_missing_values(df)
    df = create_engineered_features(df)
    df = encode_categoricals(df)
    X, y, df_final = prepare_datasets(df)
    save_files(X, y, df_final)
    print_summary(X, y)


if __name__ == "__main__":
    main()
