"""
NHANES PROJECT - STEP 4
Train 3 ML Models for all 6 prediction targets
Shows clear score comparison for all 3 models
"""

import pandas as pd
import numpy as np
import os
import pickle
import warnings
warnings.filterwarnings('ignore')

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score
)
from xgboost import XGBClassifier

# ── CONFIG ────────────────────────────────────────────────────────────────────
FEATURES_PATH = "data/X_features.csv"
TARGETS_PATH  = "data/y_targets.csv"
MODELS_DIR    = "models"
RESULTS_DIR   = "results"

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ── 7 PREDICTION TARGETS ──────────────────────────────────────────────────────
TARGETS = {
    "diabetes_diagnosed"    : {"type": "binary",     "name": "Diabetes Risk"},
    "cvd_history"           : {"type": "binary",     "name": "Cardiovascular Risk"},
    "hypertension_diagnosed": {"type": "binary",     "name": "Hypertension Risk"},
    "metabolic_syndrome"    : {"type": "binary",     "name": "Metabolic Syndrome"},
    "diabetes_stage"        : {"type": "multiclass", "name": "Diabetes Stage"},
    "hypertension_stage"    : {"type": "multiclass", "name": "Hypertension Stage"},
    "obesity_stage"         : {"type": "multiclass", "name": "Obesity Stage"},
}

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
def load_data():
    print("=" * 75)
    print("   NHANES HEALTH PREDICTION — MODEL TRAINING")
    print("=" * 75)

    X = pd.read_csv(FEATURES_PATH)
    y = pd.read_csv(TARGETS_PATH)
    y = y.drop(columns=['SEQN'], errors='ignore')

    # Drop low-signal feature (99% zeros)
    if 'fast_food_times_per_week' in X.columns:
        X = X.drop(columns=['fast_food_times_per_week'])

    X = X.fillna(X.median(numeric_only=True))

    print(f"\n   Dataset: {len(X):,} samples | {X.shape[1]} features | 7 prediction targets")
    print(f"   Training 3 models per target → 21 models total\n")
    return X, y


# ── GET SCORES ────────────────────────────────────────────────────────────────
def get_scores(model, X_test, y_test, target_type):
    y_pred = model.predict(X_test)
    acc    = accuracy_score(y_test, y_pred) * 100
    prec   = precision_score(y_test, y_pred, average='weighted', zero_division=0) * 100
    rec    = recall_score(y_test, y_pred, average='weighted', zero_division=0) * 100
    f1     = f1_score(y_test, y_pred, average='weighted', zero_division=0) * 100
    try:
        if target_type == "binary":
            prob  = model.predict_proba(X_test)[:, 1]
            auc   = roc_auc_score(y_test, prob) * 100
        else:
            prob  = model.predict_proba(X_test)
            auc   = roc_auc_score(y_test, prob, multi_class='ovr', average='weighted') * 100
    except Exception:
        auc = 0.0
    return {
        "accuracy" : round(acc, 1),
        "precision": round(prec, 1),
        "recall"   : round(rec, 1),
        "f1"       : round(f1, 1),
        "roc_auc"  : round(auc, 1),
    }


# ── PRINT SCORE BOX ───────────────────────────────────────────────────────────
def print_score_box(model_name, scores, is_best=False):
    star = " ★ BEST" if is_best else ""
    print(f"   ┌─────────────────────────────────────────┐")
    print(f"   │  {model_name:<36}{star:>5} │")
    print(f"   ├─────────────────────────────────────────┤")
    print(f"   │  Accuracy  : {scores['accuracy']:>5.1f}%                      │")
    print(f"   │  Precision : {scores['precision']:>5.1f}%                      │")
    print(f"   │  Recall    : {scores['recall']:>5.1f}%                      │")
    print(f"   │  F1 Score  : {scores['f1']:>5.1f}%                      │")
    print(f"   │  ROC-AUC   : {scores['roc_auc']:>5.1f}%  ← main score       │")
    print(f"   └─────────────────────────────────────────┘")


# ── TRAIN ONE TARGET ──────────────────────────────────────────────────────────
def train_target(target_col, target_info, X, y, all_results):
    target_name = target_info["name"]
    target_type = target_info["type"]

    print(f"\n{'━'*75}")
    print(f"   🎯  {target_name.upper()}")
    print(f"{'━'*75}")

    # Prepare data
    y_target = y[target_col].dropna().astype(int)
    X_target = X.loc[y_target.index].reset_index(drop=True)
    y_target = y_target.reset_index(drop=True)

    # Class distribution
    dist = y_target.value_counts().sort_index().to_dict()
    total = len(y_target)
    print(f"\n   Samples: {total:,}  |  Class distribution: {dist}")

    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X_target, y_target,
        test_size=0.2,
        random_state=42,
        stratify=y_target
    )
    print(f"   Train: {len(X_train):,}  |  Test: {len(X_test):,}  (80/20 stratified split)")

    # Scale for Logistic Regression
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    # ── MODEL 1: LOGISTIC REGRESSION ─────────────────────────────────────────
    print(f"\n   Training Model 1/3: Logistic Regression...")
    lr = LogisticRegression(
        class_weight='balanced',
        max_iter=1000,
        random_state=42
    )
    lr.fit(X_train_sc, y_train)
    lr_scores = get_scores(lr, X_test_sc, y_test, target_type)

    # ── MODEL 2: RANDOM FOREST ────────────────────────────────────────────────
    print(f"   Training Model 2/3: Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=100,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train.values, y_train)
    rf_scores = get_scores(rf, X_test.values, y_test, target_type)

    # ── MODEL 3: XGBOOST ──────────────────────────────────────────────────────
    print(f"   Training Model 3/3: XGBoost...")
    if target_type == "binary":
        pos = len(y_train[y_train == 1])
        neg = len(y_train[y_train == 0])
        spw = neg / max(pos, 1)
        xgb = XGBClassifier(
            n_estimators=100,
            scale_pos_weight=spw,
            random_state=42,
            eval_metric='logloss',
            verbosity=0
        )
    else:
        xgb = XGBClassifier(
            n_estimators=100,
            objective='multi:softprob',
            num_class=len(y_target.unique()),
            random_state=42,
            eval_metric='mlogloss',
            verbosity=0
        )
    xgb.fit(X_train.values, y_train)
    xgb_scores = get_scores(xgb, X_test.values, y_test, target_type)

    # ── SHOW ALL 3 SCORES ─────────────────────────────────────────────────────
    print(f"\n   ── SCORES ──────────────────────────────────────────────────────\n")

    # Find best by ROC-AUC
    scores_dict = {
        "Logistic Regression": lr_scores,
        "Random Forest"      : rf_scores,
        "XGBoost"            : xgb_scores
    }
    best_name = max(scores_dict, key=lambda k: scores_dict[k]['roc_auc'])

    print_score_box("Logistic Regression", lr_scores,  is_best=(best_name == "Logistic Regression"))
    print()
    print_score_box("Random Forest",       rf_scores,  is_best=(best_name == "Random Forest"))
    print()
    print_score_box("XGBoost",             xgb_scores, is_best=(best_name == "XGBoost"))

    # ── TOP FEATURES (from best tree model) ───────────────────────────────────
    best_tree = xgb if best_name == "XGBoost" else rf
    feat_imp = pd.Series(
        best_tree.feature_importances_,
        index=X_target.columns
    ).sort_values(ascending=False).head(5)

    print(f"\n   Top 5 features driving {target_name}:")
    for feat, imp in feat_imp.items():
        bar = "▓" * int(imp * 50)
        print(f"   {feat:<35} {imp:.3f}  {bar}")

    # ── SAVE BEST MODEL ───────────────────────────────────────────────────────
    best_model  = {"Logistic Regression": lr, "Random Forest": rf, "XGBoost": xgb}[best_name]
    best_scaler = scaler if best_name == "Logistic Regression" else None
    best_scores = scores_dict[best_name]

    model_path = os.path.join(MODELS_DIR, f"{target_col}_best_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump({
            "model"      : best_model,
            "scaler"     : best_scaler,
            "model_name" : best_name,
            "target_col" : target_col,
            "target_name": target_name,
            "target_type": target_type,
            "features"   : list(X_target.columns),
            "metrics"    : best_scores,
            "class_dist" : dist
        }, f)

    print(f"\n   ✓ Best model saved → models/{target_col}_best_model.pkl")

    # Store for final summary
    all_results.append({
        "target"     : target_name,
        "best_model" : best_name,
        "lr_auc"     : lr_scores['roc_auc'],
        "rf_auc"     : rf_scores['roc_auc'],
        "xgb_auc"    : xgb_scores['roc_auc'],
        "best_auc"   : best_scores['roc_auc'],
        "best_f1"    : best_scores['f1'],
        "best_acc"   : best_scores['accuracy'],
    })

    # Save CSV for this target
    target_csv = os.path.join(RESULTS_DIR, f"{target_col}_scores.csv")
    pd.DataFrame([
        {"model": "Logistic Regression", **lr_scores},
        {"model": "Random Forest",       **rf_scores},
        {"model": "XGBoost",             **xgb_scores},
    ]).to_csv(target_csv, index=False)


# ── FINAL SUMMARY TABLE ───────────────────────────────────────────────────────
def print_final_summary(all_results):
    print(f"\n\n{'━'*75}")
    print(f"   FINAL SUMMARY — ALL 6 TARGETS")
    print(f"{'━'*75}")

    print(f"\n   {'Target':<28} {'Best Model':<22} {'LR AUC':>7} {'RF AUC':>7} {'XGB AUC':>8} {'BEST AUC':>9}")
    print(f"   {'─'*28} {'─'*22} {'─'*7} {'─'*7} {'─'*8} {'─'*9}")

    for r in all_results:
        print(f"   {r['target']:<28} {r['best_model']:<22} "
              f"{r['lr_auc']:>7.1f} {r['rf_auc']:>7.1f} "
              f"{r['xgb_auc']:>8.1f} {r['best_auc']:>9.1f}")

    print(f"\n   All scores saved in: results/")
    print(f"   All models saved in: models/")
    print(f"\n{'━'*75}")
    print(f"   ✅  STEP 4 COMPLETE")
    print(f"{'━'*75}")
    print(f"\n   Next → python 5_ai_advice.py\n")

    # Save full summary
    pd.DataFrame(all_results).to_csv(
        os.path.join(RESULTS_DIR, "full_summary.csv"), index=False
    )
    print(f"   Summary saved → results/full_summary.csv")


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    X, y = load_data()

    all_results = []

    for target_col, target_info in TARGETS.items():
        train_target(target_col, target_info, X, y, all_results)

    print_final_summary(all_results)


if __name__ == "__main__":
    main()
