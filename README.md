# ⚕ HealthAI — Clinical Risk Prediction Platform

> **Machine Learning Health Risk Prediction Platform trained on NHANES 2021–2023 data**  
> Predicts 7 cardiometabolic conditions and delivers personalised AI health advice through an interactive web dashboard.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://nhanes-health-ai.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)](https://mysql.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-latest-green.svg)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-latest-red.svg)](https://xgboost.readthedocs.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌐 Live Demo

**👉 [nhanes-health-ai.streamlit.app](https://healthai-clinical-risk-studio.streamlit.app/)**

Enter any patient's health measurements and get instant risk predictions across 7 conditions with personalised health advice.

---

## 📋 Table of Contents

- [Overview](#overview)
- [7 Prediction Targets](#7-prediction-targets)
- [Dataset](#dataset)
- [Project Pipeline](#project-pipeline)
- [Feature Engineering](#feature-engineering)
- [Model Performance](#model-performance)
- [Dashboard Pages](#dashboard-pages)
- [Project Structure](#project-structure)
- [How to Run Locally](#how-to-run-locally)
- [Tech Stack](#tech-stack)
- [Key Findings](#key-findings)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)

---

## Overview

This project builds a complete end-to-end machine learning pipeline using the **NHANES 2021–2023** (National Health and Nutrition Examination Survey) dataset published by the **CDC (Centers for Disease Control and Prevention, USA)**.

The platform:
- Trains **21 ML models** (3 algorithms × 7 targets) on **6,235 real patient records**
- Predicts **7 cardiometabolic health conditions** per patient
- Generates a **personalised 6-section health report** based on ADA, AHA, and WHO clinical guidelines
- Delivers everything through a **professional 7-page Streamlit dashboard**

---

## 7 Prediction Targets

| # | Condition | Type | Best Model | ROC-AUC |
|---|---|---|---|---|
| 1 | 🩸 Diabetes Risk | Binary | Random Forest | **92.4%** |
| 2 | ❤️ Cardiovascular Risk | Binary | Logistic Regression | **81.2%** |
| 3 | 💉 Hypertension Risk | Binary | Logistic Regression | **82.7%** |
| 4 | ⚠️ Metabolic Syndrome | Binary | XGBoost | **99.9%** |
| 5 | 📊 Diabetes Stage | 3-class | XGBoost | **98.9%** |
| 6 | 📈 Hypertension Stage | 4-class | Random Forest | **100%** |
| 7 | ⚖️ Obesity Stage | 4-class | Random Forest | **100%** |

> ⚠️ **Note:** Obesity Stage and Hypertension Stage show 100% AUC due to **data leakage** — their labels are derived directly from BMI and blood pressure values already present as features. The most clinically meaningful models are Diabetes Risk (92.4%), CVD Risk (81.2%), and Hypertension Risk (82.7%).

---

## Dataset

**Source:** [CDC NHANES 2021–2023](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?Cycle=2021-2023)

| Category | Files | Key Variables |
|---|---|---|
| Demographics | DEMO_L | Age, gender, race, education, income |
| Examination | BMX_L, BPXO_L | BMI, weight, height, waist, blood pressure |
| Laboratory | GHB_L, GLU_L, HDL_L, TRIGLY_L, TCHOL_L, INS_L, HSCRP_L | HbA1c, glucose, insulin, lipids, CRP |
| Questionnaire | DIQ_L, MCQ_L, BPQ_L, PAQ_L, SMQ_L, ALQ_L, DBQ_L, DPQ_L, SLQ_L | Disease history, lifestyle, depression, sleep |

- **Total files:** 19 XPT files
- **Original records:** 11,933 respondents
- **After cleaning:** 6,235 examined adults aged 18–80

---

## Project Pipeline

```
Step 1 → 1_load_to_sql.py      Load 19 XPT files into MySQL (19 tables)
Step 2 → 2_clean_merge.sql     SQL cleaning + merge → 6,235 clean rows
Step 3 → 3_features.py         Feature engineering → 60 features
Step 4 → 4_train_models.py     Train 21 ML models → save 7 best .pkl files
Step 5 → 5_ai_advice.py        AI health advice engine (standalone)
Step 6 → 6_dashboard.py        Streamlit multi-page web dashboard
```

---

## Feature Engineering

11 new features created from raw clinical data:

| Feature | Formula | Clinical Significance |
|---|---|---|
| `homa_ir` | (Glucose × Insulin) / 405 | Insulin resistance index |
| `total_hdl_ratio` | Total Cholesterol / HDL | Cardiovascular risk marker |
| `ldl_hdl_ratio` | LDL / HDL | Atherogenic index |
| `pulse_pressure` | Systolic BP − Diastolic BP | Arterial stiffness |
| `waist_height_ratio` | Waist / Height | Better obesity predictor than BMI alone |
| `avg_sleep_hours` | (Weekday×5 + Weekend×2) / 7 | Weighted weekly sleep |
| `total_activity_min` | Moderate + Vigorous minutes | Total weekly activity |
| `bmi_category` | WHO cut-points | Underweight/Normal/Overweight/Obese |
| `age_group` | Age cut-points | 18-34 / 35-49 / 50-64 / 65+ |
| `activity_level` | Minutes/week | Sedentary/Low/Moderate/High |
| `depression_category` | PHQ-9 score | None/Mild/Moderate/Severe |

---

## Model Performance

Three algorithms were trained and compared for each target:

| Target | LR AUC | RF AUC | XGB AUC | **Best** |
|---|---|---|---|---|
| Diabetes Risk | 91.2% | **92.4%** | 92.2% | Random Forest |
| CVD Risk | **81.2%** | 81.0% | 78.1% | Logistic Regression |
| Hypertension Risk | **82.7%** | 82.3% | 81.0% | Logistic Regression |
| Metabolic Syndrome | 93.7% | 97.6% | **99.9%** | XGBoost |
| Diabetes Stage | 91.1% | 98.3% | **98.9%** | XGBoost |
| Hypertension Stage | 96.6% | **100%** | 100% | Random Forest |
| Obesity Stage | 99.8% | **100%** | 100% | Random Forest |

**Training strategy:**
- 80/20 stratified train/test split
- `class_weight='balanced'` for Logistic Regression and Random Forest
- `scale_pos_weight` in XGBoost for class imbalance
- Best model per target saved as `.pkl` file

---

## Dashboard Pages

| Page | Description |
|---|---|
| 📋 Overview | All 7 predictions, patient profile, overall summary |
| 🩸 Diabetes | HbA1c, glucose, HOMA-IR, ADA clinical thresholds |
| ❤️ Cardiovascular | Lipid panel, CRP, cholesterol ratios, AHA guidelines |
| 💉 Hypertension | BP readings, staging, pulse pressure, AHA BP table |
| ⚠️ Metabolic Syndrome | 5-criteria check, IDF/AHA/NHLBI guidelines |
| 📊 Health Risk Score | Composite 0–100 risk score, factor breakdown |
| 🌿 Lifestyle Impact | Activity, sleep, smoking, alcohol, depression analysis |

---

## Project Structure

```
nhanes-health-ai/
│
├── 6_dashboard.py                    # Streamlit web dashboard (main app)
├── 5_ai_advice.py                    # Standalone AI health advice generator
├── 4_train_models.py                 # ML model training script
├── 3_features.py                     # Feature engineering pipeline
├── 2_clean_merge.sql                 # SQL data cleaning and merging
├── 1_load_to_sql.py                  # XPT → MySQL loader
├── requirements.txt                  # Python dependencies
│
└── models/
    ├── diabetes_diagnosed_best_model.pkl
    ├── cvd_history_best_model.pkl
    ├── hypertension_diagnosed_best_model.pkl
    ├── metabolic_syndrome_best_model.pkl
    ├── diabetes_stage_best_model.pkl
    ├── hypertension_stage_best_model.pkl
    └── obesity_stage_best_model.pkl
```

---

## How to Run Locally

### Prerequisites
- Python 3.11+
- MySQL 8.0
- MySQL Workbench

### 1. Clone the repository
```bash
git clone https://github.com/itzmevishwa/HealthAI-Clinical-Risk-Studio.git
cd HealthAI-Clinical-Risk-Studio
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install sqlalchemy pymysql pyreadstat
```

### 4. Download NHANES data
Download the 19 XPT files from [CDC NHANES 2021–2023](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?Cycle=2021-2023) into `data/raw/`

### 5. Set up MySQL
Create database in MySQL Workbench:
```sql
CREATE DATABASE nhanes_project;
```

### 6. Run the pipeline
```bash
# Step 1: Load data into MySQL
python 1_load_to_sql.py

# Step 2: Clean and merge (run in MySQL Workbench)
# Open 2_clean_merge.sql and execute

# Step 3: Feature engineering
python 3_features.py

# Step 4: Train models
python 4_train_models.py

# Step 5: Run dashboard
streamlit run 6_dashboard.py
```

Open `http://localhost:8501` in your browser.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Database** | MySQL 8.0, SQL, MySQL Workbench |
| **Connection** | SQLAlchemy, PyMySQL |
| **Data Processing** | Python 3.11, pandas, numpy |
| **Machine Learning** | scikit-learn, XGBoost |
| **Dashboard** | Streamlit |
| **Model Storage** | pickle (.pkl files) |

---

## Key Findings

### Dataset Statistics
- **40.5%** of participants were obese (BMI ≥ 30) — matches US national rate
- **36.1%** had combined diabetes or prediabetes by HbA1c criteria
- **53.3%** had elevated or hypertensive blood pressure
- **Only 14.2%** met the WHO 150 min/week physical activity guideline
- **7.7%** had cardiovascular disease history

### Model Insights
- `hba1c` is the single most important feature for diabetes prediction (importance: 0.375)
- `age` is the strongest cardiovascular risk predictor (importance: 0.101)
- `systolic_bp` + `diastolic_bp` together explain 56% of hypertension stage variance
- `homa_ir` and `waist_height_ratio` are top features for metabolic syndrome

---

## Limitations

- **Cross-sectional data** — no longitudinal follow-up to verify disease development
- **US population only** — findings may not generalise to other countries
- **Data leakage** in obesity and hypertension stage models — labels derived from features
- **~50% missing** for fasting labs (glucose, insulin, triglycerides) — fasting tests only
- **CVD model** limited by small positive class (7.7%, n=478)

---

## Future Improvements

- [ ] SHAP explainability — per-patient feature importance
- [ ] Claude/GPT API integration for dynamic AI health narratives
- [ ] MLflow experiment tracking and model versioning
- [ ] FastAPI REST backend for hospital system integration
- [ ] SMOTE oversampling for CVD model improvement
- [ ] Additional NHANES modules — kidney function (BIOPRO_L), CBC (CBC_L)
- [ ] PDF export for health reports
- [ ] Multi-language support

---

## Data Source

This project uses publicly available data from:

**National Health and Nutrition Examination Survey (NHANES) 2021–2023**  
Centers for Disease Control and Prevention (CDC), National Center for Health Statistics (NCHS)  
[https://www.cdc.gov/nchs/nhanes](https://www.cdc.gov/nchs/nhanes)

---

## Disclaimer

> This platform is built on NHANES 2021–2023 data for **educational and research purposes only**. It does **NOT** constitute medical advice. Always consult a qualified healthcare professional for clinical decisions.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ during Data Science & Machine Learning Internship**

[![GitHub](https://img.shields.io/badge/GitHub-itzmevishwa-black?logo=github)](https://github.com/itzmevishwa)
[![Live App](https://img.shields.io/badge/Live-nhanes--health--ai.streamlit.app-FF4B4B?logo=streamlit)](https://healthai-clinical-risk-studio.streamlit.app/)

</div>
