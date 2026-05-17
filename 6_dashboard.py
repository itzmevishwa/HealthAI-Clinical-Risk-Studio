"""
NHANES PROJECT - STEP 6  (UPGRADED)
HealthAI Clinical Risk Studio — Elegant Professional Dashboard
Run: streamlit run 6_dashboard.py
"""

import streamlit as st
import pickle
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HealthAI — Clinical Risk Studio",
    page_icon="⚕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── MASTER CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── RESET & TOKENS ── */
:root {
  --c0:#060c1a; --c1:#0b1628; --c2:#0f1e36;
  --panel:rgba(11,22,40,0.95);
  --border:rgba(148,163,184,0.13);
  --border-bright:rgba(56,189,248,0.28);
  --text-1:#f1f5f9; --text-2:#cbd5e1; --text-3:#94a3b8;
  --teal:#22d3ee; --teal-dim:rgba(34,211,238,0.14);
  --green:#34d399; --green-dim:rgba(52,211,153,0.12);
  --amber:#fbbf24; --amber-dim:rgba(251,191,36,0.12);
  --rose:#fb7185; --rose-dim:rgba(251,113,133,0.12);
  --blue:#60a5fa; --blue-dim:rgba(96,165,250,0.12);
  --shadow:0 24px 64px rgba(0,0,0,0.55);
  --shadow-sm:0 8px 24px rgba(0,0,0,0.35);
  --r:14px;
}

*,::before,::after{box-sizing:border-box;}
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;-webkit-font-smoothing:antialiased;}

/* ── BACKGROUND ── */
.stApp{
  background:
    radial-gradient(ellipse 900px 600px at 15% -5%, rgba(34,211,238,0.10) 0%, transparent 65%),
    radial-gradient(ellipse 700px 500px at 85% 5%,  rgba(52,211,153,0.09) 0%, transparent 65%),
    radial-gradient(ellipse 500px 400px at 50% 90%, rgba(96,165,250,0.07) 0%, transparent 65%),
    linear-gradient(180deg,#060c1a 0%,#0b1628 55%,#060c1a 100%) !important;
}

/* ── MAIN CONTAINER ── */
.main .block-container{
  padding:1.4rem 2.2rem 3rem!important;
  max-width:1320px!important;
}

/* ── HIDE JUNK ── */
#MainMenu,footer,header,.stDeployButton,[data-testid="stSidebar"],[data-testid="collapsedControl"]{
  display:none!important;visibility:hidden!important;
}

/* ── ANIMATIONS ── */
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:200% 50%}100%{background-position:-200% 50%}}
@keyframes pulseRing{0%,100%{box-shadow:0 0 0 0 rgba(34,211,238,0)}50%{box-shadow:0 0 0 6px rgba(34,211,238,0.12)}}
@keyframes gradFlow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}

/* ── HERO ── */
.hero{
  background:linear-gradient(135deg,rgba(11,22,40,0.98),rgba(6,12,26,0.92));
  border:1px solid var(--border);
  border-top:1px solid rgba(34,211,238,0.22);
  border-radius:20px;
  padding:2rem 2.4rem;
  display:flex;align-items:center;justify-content:space-between;gap:2rem;
  box-shadow:var(--shadow);backdrop-filter:blur(20px);
  position:relative;overflow:hidden;
  animation:fadeUp .6s ease both;
}
.hero::before{
  content:"";position:absolute;top:-120px;right:-80px;
  width:420px;height:420px;border-radius:50%;
  background:radial-gradient(circle,rgba(34,211,238,0.07) 0%,transparent 70%);
  pointer-events:none;
}
.hero::after{
  content:"";position:absolute;bottom:-80px;left:30%;
  width:360px;height:360px;border-radius:50%;
  background:radial-gradient(circle,rgba(52,211,153,0.05) 0%,transparent 70%);
  pointer-events:none;
}
.hero-eyebrow{
  font-size:11px;letter-spacing:.2em;text-transform:uppercase;
  color:var(--teal);font-weight:600;margin-bottom:.4rem;
}
.hero-title{
  font-family:'Space Grotesk',sans-serif;
  font-size:2.1rem;font-weight:700;line-height:1.1;
  background:linear-gradient(135deg,#f1f5f9 0%,#93c5fd 40%,#34d399 100%);
  background-size:200% 200%;animation:gradFlow 8s ease infinite;
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  margin-bottom:.5rem;
}
.hero-sub{font-size:.95rem;color:var(--text-3);line-height:1.65;max-width:480px;}
.hero-pills{display:flex;flex-wrap:wrap;gap:8px;margin-top:1rem;}
.pill{
  font-size:11px;font-weight:600;padding:4px 12px;border-radius:999px;
  letter-spacing:.04em;
  background:var(--teal-dim);color:#a5f3fc;
  border:1px solid rgba(34,211,238,0.25);
}
.pill.g{background:var(--green-dim);color:#bbf7d0;border-color:rgba(52,211,153,0.28);}
.pill.a{background:var(--amber-dim);color:#fde68a;border-color:rgba(251,191,36,0.28);}

.hero-stats{
  display:grid;grid-template-columns:repeat(2,1fr);gap:.7rem;flex-shrink:0;
}
.hstat{
  background:rgba(6,12,26,0.7);border:1px solid var(--border);
  border-radius:12px;padding:.75rem 1rem;
}
.hstat-label{font-size:10px;text-transform:uppercase;letter-spacing:.14em;color:var(--text-3);font-weight:600;}
.hstat-value{font-family:'Space Grotesk',sans-serif;font-size:1.45rem;color:var(--text-1);font-weight:700;margin-top:2px;}

/* ── NAV RADIO PILLS ── */
div[role="radiogroup"]{
  display:flex!important;flex-wrap:wrap!important;gap:5px!important;
  background:rgba(6,12,26,0.7)!important;border:1px solid var(--border)!important;
  padding:5px!important;border-radius:999px!important;
  box-shadow:var(--shadow-sm)!important;backdrop-filter:blur(12px);
}
div[role="radiogroup"] label{
  border-radius:999px!important;padding:6px 16px!important;
  font-size:13px!important;font-weight:600!important;color:var(--text-3)!important;
  cursor:pointer;transition:all .2s ease;
}
div[role="radiogroup"] label:has(input:checked){
  background:linear-gradient(135deg,var(--teal),var(--green))!important;
  color:#06101b!important;
  box-shadow:0 6px 20px rgba(34,211,238,0.28)!important;
  animation:pulseRing 2.5s ease-in-out infinite;
}

/* ── METRICS ── */
[data-testid="stMetric"]{
  background:var(--panel)!important;
  border:1px solid var(--border)!important;
  border-radius:var(--r)!important;
  padding:1.1rem 1.3rem!important;
  box-shadow:var(--shadow-sm)!important;
  transition:transform .2s,box-shadow .2s;
  animation:fadeUp .45s ease both;
}
[data-testid="stMetric"]:hover{
  transform:translateY(-3px);
  box-shadow:0 16px 36px rgba(0,0,0,0.45)!important;
  border-color:var(--border-bright)!important;
}
[data-testid="stMetricLabel"]{
  font-size:11px!important;text-transform:uppercase!important;
  letter-spacing:.14em!important;color:var(--text-3)!important;font-weight:600!important;
}
[data-testid="stMetricValue"]{
  font-family:'Space Grotesk',sans-serif!important;
  font-size:1.65rem!important;color:var(--text-1)!important;font-weight:700!important;
}
[data-testid="stMetricDelta"]{font-size:12px!important;font-weight:600!important;}

/* ── ALERT BOXES ── */
.stSuccess,.stInfo,.stWarning,.stError{
  border-radius:12px!important;font-size:14px!important;font-weight:500!important;
  backdrop-filter:blur(8px)!important;
  box-shadow:var(--shadow-sm)!important;
  transition:transform .2s,box-shadow .2s;
  animation:fadeUp .4s ease both;
}
.stSuccess:hover,.stInfo:hover,.stWarning:hover,.stError:hover{
  transform:translateY(-2px);
  box-shadow:0 14px 30px rgba(0,0,0,0.45)!important;
}
.stSuccess{background:rgba(52,211,153,0.10)!important;border:1px solid rgba(52,211,153,0.28)!important;}
.stInfo{background:rgba(56,189,248,0.10)!important;border:1px solid rgba(56,189,248,0.26)!important;}
.stWarning{background:rgba(251,191,36,0.10)!important;border:1px solid rgba(251,191,36,0.28)!important;}
.stError{background:rgba(251,113,133,0.10)!important;border:1px solid rgba(251,113,133,0.28)!important;}

/* ── PROGRESS ── */
.stProgress>div>div{
  background:rgba(148,163,184,0.15)!important;border-radius:30px!important;
}
.stProgress>div>div>div>div{
  border-radius:30px!important;
  background:linear-gradient(90deg,var(--teal),var(--green))!important;
  background-size:200% 200%!important;
  animation:gradFlow 4s ease infinite;
}

/* ── BUTTON ── */
.stButton>button,.stFormSubmitButton>button{
  background:linear-gradient(135deg,var(--teal) 0%,var(--green) 100%)!important;
  color:#06101b!important;border:none!important;border-radius:12px!important;
  padding:.85rem 2rem!important;font-size:15px!important;font-weight:700!important;
  letter-spacing:.03em!important;width:100%!important;
  box-shadow:0 10px 28px rgba(34,211,238,0.3)!important;
  background-size:200% 200%!important;animation:gradFlow 6s ease infinite;
  transition:transform .2s,box-shadow .2s!important;
}
.stButton>button:hover,.stFormSubmitButton>button:hover{
  transform:translateY(-2px)!important;
  box-shadow:0 16px 36px rgba(34,211,238,0.38)!important;
}

/* ── FORM ── */
div[data-testid="stForm"]{
  background:var(--panel)!important;border:1px solid var(--border)!important;
  border-radius:18px!important;padding:1.5rem 1.8rem!important;
  box-shadow:var(--shadow)!important;backdrop-filter:blur(16px);
  animation:fadeUp .5s ease both;
}
div[data-testid="stExpander"]{
  background:rgba(6,12,26,0.65)!important;border:1px solid var(--border)!important;
  border-radius:12px!important;overflow:hidden;
}
div[data-testid="stExpander"] summary{
  font-size:14px!important;font-weight:600!important;color:var(--text-2)!important;
}

/* ── INPUTS ── */
.stNumberInput input,.stTextInput input,.stSelectbox>div>div{
  background:rgba(6,12,26,0.8)!important;
  border:1px solid var(--border)!important;
  color:var(--text-1)!important;border-radius:10px!important;font-size:14px!important;
  transition:border-color .2s,box-shadow .2s;
}
.stNumberInput input:focus,.stTextInput input:focus{
  border-color:rgba(34,211,238,0.5)!important;
  box-shadow:0 0 0 3px rgba(34,211,238,0.12)!important;
}
label,.stMarkdown p{color:var(--text-2)!important;}
.stMarkdown h2{color:var(--text-1)!important;font-family:'Space Grotesk',sans-serif!important;font-size:1.55rem!important;}
.stMarkdown h3{color:var(--text-1)!important;font-family:'Space Grotesk',sans-serif!important;font-size:1.15rem!important;}
.stCaption,.stMarkdown small{color:var(--text-3)!important;}
hr{border-color:rgba(148,163,184,0.1)!important;margin:1.2rem 0!important;}

/* ── TABS (inside pages) ── */
.stTabs [data-baseweb="tab-list"]{
  background:rgba(6,12,26,0.6)!important;border-radius:12px!important;
  padding:5px!important;gap:4px!important;
  border:1px solid var(--border)!important;
}
.stTabs [data-baseweb="tab"]{
  border-radius:9px!important;padding:8px 18px!important;
  font-size:13px!important;font-weight:600!important;
  color:var(--text-3)!important;border:none!important;
}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg,rgba(34,211,238,0.18),rgba(52,211,153,0.15))!important;
  color:var(--teal)!important;border:1px solid rgba(34,211,238,0.25)!important;
}

/* ── CUSTOM COMPONENTS ── */
.inline-bmi{
  display:inline-flex;align-items:center;gap:8px;
  background:var(--teal-dim);border:1px solid rgba(34,211,238,0.22);
  color:#a5f3fc;padding:.45rem .9rem;border-radius:10px;font-size:.85rem;
  font-weight:600;margin:.5rem 0 .8rem;
}
.section-head{
  display:flex;align-items:center;gap:10px;margin:1.6rem 0 .9rem;
}
.section-dot{
  width:8px;height:8px;border-radius:50%;background:var(--teal);
  box-shadow:0 0 10px rgba(34,211,238,0.6);
  animation:pulseRing 2s ease infinite;flex-shrink:0;
}
.section-title{
  font-family:'Space Grotesk',sans-serif;font-size:1rem;
  font-weight:700;color:var(--text-1);letter-spacing:.02em;
}
.risk-tag{
  display:inline-flex;align-items:center;gap:5px;
  padding:3px 10px;border-radius:999px;font-size:11px;font-weight:700;
  letter-spacing:.04em;margin-bottom:8px;
}
.risk-low{background:var(--green-dim);color:#86efac;border:1px solid rgba(52,211,153,0.25);}
.risk-med{background:var(--amber-dim);color:#fde68a;border:1px solid rgba(251,191,36,0.25);}
.risk-high{background:var(--rose-dim);color:#fda4af;border:1px solid rgba(251,113,133,0.25);}
.score-ring{
  width:120px;height:120px;border-radius:50%;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  font-family:'Space Grotesk',sans-serif;
  border:3px solid;margin:0 auto 1rem;
}
.score-number{font-size:2rem;font-weight:700;line-height:1;}
.score-label{font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;margin-top:2px;}

@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;}}
@media(max-width:900px){
  .hero{flex-direction:column;}
  .hero-stats{width:100%;grid-template-columns:repeat(2,1fr);}
}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ─────────────────────────────────────────────────────────────────
MODELS_DIR = "models"
MODEL_FILES = {
    "diabetes_diagnosed"    : "diabetes_diagnosed_best_model.pkl",
    "cvd_history"           : "cvd_history_best_model.pkl",
    "hypertension_diagnosed": "hypertension_diagnosed_best_model.pkl",
    "metabolic_syndrome"    : "metabolic_syndrome_best_model.pkl",
    "diabetes_stage"        : "diabetes_stage_best_model.pkl",
    "hypertension_stage"    : "hypertension_stage_best_model.pkl",
    "obesity_stage"         : "obesity_stage_best_model.pkl",
}
LABEL_MAPS = {
    "diabetes_diagnosed"    : {0:"No Diabetes",           1:"Diabetes Likely"},
    "cvd_history"           : {0:"Low CVD Risk",          1:"High CVD Risk"},
    "hypertension_diagnosed": {0:"No Hypertension",       1:"Hypertension Likely"},
    "metabolic_syndrome"    : {0:"No Metabolic Syndrome", 1:"Metabolic Syndrome"},
    "diabetes_stage"        : {0:"Normal",1:"Prediabetes",2:"Diabetes"},
    "hypertension_stage"    : {0:"Normal BP",1:"Elevated",2:"Stage 1 HTN",3:"Stage 2 HTN"},
    "obesity_stage"         : {0:"Underweight",1:"Normal Weight",2:"Overweight",3:"Obese"},
}

# ── LOAD MODELS ───────────────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    models = {}
    for target, fname in MODEL_FILES.items():
        path = os.path.join(MODELS_DIR, fname)
        if os.path.exists(path):
            with open(path, "rb") as f:
                models[target] = pickle.load(f)
    return models

# ── FEATURE ENGINEERING ───────────────────────────────────────────────────────
def prepare_features(person, model_obj):
    p = person.copy()
    p["total_hdl_ratio"]    = p["total_cholesterol"] / max(p["hdl_cholesterol"], 1)
    p["ldl_hdl_ratio"]      = p["ldl_cholesterol"]   / max(p["hdl_cholesterol"], 1)
    p["pulse_pressure"]     = p["systolic_bp"] - p["diastolic_bp"]
    p["homa_ir"]            = (p["fasting_glucose"] * p["fasting_insulin"]) / 405
    p["waist_height_ratio"] = p["waist_cm"] / p["height_cm"]
    p["avg_sleep_hours"]    = (p["sleep_hours_weekday"]*5 + p["sleep_hours_weekend"]*2) / 7
    p["total_activity_min"] = p["moderate_activity_min"] + p["vigorous_activity_min"]
    p["smoking_intensity"]  = p["cigarettes_per_day"]

    bmi = p["bmi"]
    bc  = "Underweight" if bmi<18.5 else "Normal" if bmi<25 else "Overweight" if bmi<30 else "Obese"
    p["bmi_category_Normal"]     = 1 if bc=="Normal"     else 0
    p["bmi_category_Overweight"] = 1 if bc=="Overweight" else 0
    p["bmi_category_Obese"]      = 1 if bc=="Obese"      else 0
    p["bmi_category_Unknown"]    = 0

    age = p["age"]
    ag  = "18-34" if age<35 else "35-49" if age<50 else "50-64" if age<65 else "65+"
    p["age_group_35-49"]   = 1 if ag=="35-49" else 0
    p["age_group_50-64"]   = 1 if ag=="50-64" else 0
    p["age_group_65+"]     = 1 if ag=="65+"   else 0
    p["age_group_Unknown"] = 0

    act = p["total_activity_min"]
    al  = "Sedentary" if act==0 else "Low" if act<150 else "Moderate" if act<300 else "High"
    p["activity_level_Low"]      = 1 if al=="Low"      else 0
    p["activity_level_Moderate"] = 1 if al=="Moderate" else 0
    p["activity_level_High"]     = 1 if al=="High"     else 0
    p["activity_level_Unknown"]  = 0

    p["smoking_status_2"] = 1 if p["smoking_status"]==2 else 0

    ds = p["depression_score"]
    dc = "None" if ds<5 else "Mild" if ds<10 else "Moderate" if ds<15 else "Moderately Severe" if ds<20 else "Severe"
    p["depression_category_Mild"]              = 1 if dc=="Mild"              else 0
    p["depression_category_Moderate"]          = 1 if dc=="Moderate"          else 0
    p["depression_category_Moderately Severe"] = 1 if dc=="Moderately Severe" else 0
    p["depression_category_Severe"]            = 1 if dc=="Severe"            else 0

    p["gender_2"] = 1 if p["gender"]==2 else 0
    for r in [2,3,4,6]: p[f"race_{r}"]      = 1 if p["race"]==r      else 0
    for e in [2,3,4,5]: p[f"education_{e}"] = 1 if p["education"]==e else 0
    p["marital_status_2"] = 1 if p["marital_status"]==2 else 0
    p["marital_status_3"] = 1 if p["marital_status"]==3 else 0

    row = {feat: p.get(feat, 0) for feat in model_obj["features"]}
    return pd.DataFrame([row])[model_obj["features"]]

# ── PREDICT ───────────────────────────────────────────────────────────────────
def run_all_predictions(person, models):
    results = {}
    for target, model_obj in models.items():
        try:
            X      = prepare_features(person, model_obj)
            mdl    = model_obj["model"]
            scaler = model_obj["scaler"]
            X_in   = scaler.transform(X) if scaler else X.values
            pred   = mdl.predict(X_in)[0]
            prob   = mdl.predict_proba(X_in)[0]
            results[target] = {
                "prediction"   : int(pred),
                "label"        : LABEL_MAPS[target].get(int(pred), str(pred)),
                "confidence"   : round(float(max(prob))*100, 1),
                "probabilities": {LABEL_MAPS[target].get(i, str(i)): round(float(p)*100, 1)
                                  for i, p in enumerate(prob)},
                "model_used"   : model_obj["model_name"],
            }
        except:
            results[target] = {"prediction":-1,"label":"Error","confidence":0,"probabilities":{},"model_used":""}
    return results

# ── RISK HELPERS ──────────────────────────────────────────────────────────────
def risk_info(target, pred):
    if target in ["diabetes_diagnosed","cvd_history","hypertension_diagnosed","metabolic_syndrome"]:
        return ("🟢","Low Risk","low") if pred==0 else ("🔴","High Risk","high")
    if target=="diabetes_stage":
        return [("🟢","Normal","low"),("🟡","Prediabetes","med"),("🔴","Diabetes","high")][pred]
    if target=="hypertension_stage":
        return [("🟢","Normal","low"),("🟡","Elevated","med"),("🟠","Stage 1","med"),("🔴","Stage 2","high")][pred]
    if target=="obesity_stage":
        return [("🟡","Underweight","med"),("🟢","Normal","low"),("🟡","Overweight","med"),("🔴","Obese","high")][pred]
    return ("⚪","Unknown","low")

def risk_tag_html(level, text):
    cls = {"low":"risk-low","med":"risk-med","high":"risk-high"}.get(level,"risk-low")
    dot = {"low":"●","med":"●","high":"●"}.get(level,"●")
    return f'<span class="risk-tag {cls}">{dot} {text}</span>'

def section_head(title):
    st.markdown(f"""
    <div class="section-head">
      <div class="section-dot"></div>
      <div class="section-title">{title}</div>
    </div>""", unsafe_allow_html=True)

# ── ADVICE ENGINE ─────────────────────────────────────────────────────────────
def generate_advice(person, predictions):
    p, pr = person, predictions
    risks, actions, positives = [], [], []
    urgency = "routine"

    ds = pr.get("diabetes_stage",{}).get("prediction",0)
    if ds==2:
        risks.append(f"Diabetes confirmed — HbA1c {p['hba1c']}%, glucose {p['fasting_glucose']} mg/dL")
        actions.append("Monitor blood sugar daily — target fasting glucose below 126 mg/dL")
        actions.append("Low-glycemic diet — replace white rice, bread, sugar with whole grains & vegetables")
        urgency = "urgent"
    elif ds==1:
        risks.append(f"Prediabetes — HbA1c {p['hba1c']}% (normal < 5.7%)")
        actions.append("Reduce sugar & refined carbs — target HbA1c below 5.7% in 6 months")
        actions.append("Walk 30 minutes daily — reduces insulin resistance significantly")
    else:
        positives.append(f"Blood sugar is normal — HbA1c {p['hba1c']}%, glucose {p['fasting_glucose']} mg/dL")

    hs = pr.get("hypertension_stage",{}).get("prediction",0)
    if hs==3:
        risks.append(f"Stage 2 Hypertension — BP {p['systolic_bp']}/{p['diastolic_bp']} mmHg")
        actions.append("See a doctor immediately — Stage 2 hypertension needs medication evaluation")
        urgency = "urgent"
    elif hs==2:
        risks.append(f"Stage 1 Hypertension — BP {p['systolic_bp']}/{p['diastolic_bp']} mmHg")
        actions.append("Limit sodium to 2,300 mg/day — avoid processed foods, fast food, canned soups")
        actions.append("10 min daily deep breathing — clinically lowers BP by 5–8 mmHg")
    elif hs==1:
        risks.append(f"Elevated blood pressure — {p['systolic_bp']}/{p['diastolic_bp']} mmHg")
        actions.append("Increase potassium foods — bananas, spinach, sweet potatoes lower BP naturally")
    else:
        positives.append(f"Blood pressure is normal — {p['systolic_bp']}/{p['diastolic_bp']} mmHg")

    if p["hdl_cholesterol"]<40:
        risks.append(f"Low HDL — {p['hdl_cholesterol']} mg/dL (target ≥ 40 men, ≥ 50 women)")
        actions.append("Raise HDL — fatty fish twice/week, olive oil, nuts, avocado")
    elif p["hdl_cholesterol"]>=60:
        positives.append(f"Excellent HDL — {p['hdl_cholesterol']} mg/dL")

    if p["triglycerides"]>=200:
        risks.append(f"High triglycerides — {p['triglycerides']} mg/dL (target < 150)")
        actions.append("Cut alcohol, sugary drinks, refined carbs — they directly raise triglycerides")
    elif p["triglycerides"]<100:
        positives.append(f"Excellent triglycerides — {p['triglycerides']} mg/dL")

    if p["ldl_cholesterol"]>=130:
        risks.append(f"Elevated LDL — {p['ldl_cholesterol']} mg/dL (target < 100)")
        actions.append("Increase soluble fiber — oats, lentils, apples — aim for 25–30 g/day")

    obs = pr.get("obesity_stage",{}).get("prediction",0)
    if obs==3:
        risks.append(f"Obesity — BMI {p['bmi']} raises risk for diabetes, heart disease, hypertension")
        actions.append(f"Target 5–10% weight loss ({round(p['weight_kg']*.05,1)}–{round(p['weight_kg']*.10,1)} kg) — improves all markers")
    elif obs==2:
        risks.append(f"Overweight — BMI {p['bmi']} — 5–10% weight loss reduces disease risk substantially")
    else:
        positives.append(f"Body weight is healthy — BMI {p['bmi']}")

    if pr.get("metabolic_syndrome",{}).get("prediction",0)==1:
        risks.append("Metabolic syndrome — cluster of high waist, BP, glucose & cholesterol")
        actions.append("30 min moderate exercise 5×/week can reverse metabolic syndrome in 6–12 months")

    if p["c_reactive_protein"]>3.0:
        risks.append(f"Elevated CRP {p['c_reactive_protein']} mg/L — systemic inflammation")
        actions.append("Anti-inflammatory diet — turmeric, berries, leafy greens, omega-3 fatty acids")

    total_act = p["moderate_activity_min"]+p["vigorous_activity_min"]
    if total_act<150:
        actions.append(f"Increase activity from {total_act} to 150+ min/week — WHO minimum guideline")
    else:
        positives.append(f"Physical activity is good — {total_act} min/week")

    avg_sl = (p["sleep_hours_weekday"]*5+p["sleep_hours_weekend"]*2)/7
    if avg_sl<7:
        risks.append(f"Insufficient sleep — {avg_sl:.1f} hrs/night worsens blood sugar & blood pressure")
        actions.append("Target 7–9 hours sleep — consistent bedtime, no screens 1 hour before bed")
    else:
        positives.append(f"Sleep is adequate — {avg_sl:.1f} hrs/night")

    if p["smoking_status"]==1:
        risks.append("Current smoker — doubles cardiovascular risk and worsens every condition")
        actions.append("Quitting smoking is the single highest-impact health change you can make")
        urgency = "urgent"
    else:
        positives.append("Non-smoker — significantly lowers cardiovascular and cancer risk")

    if p["alcohol_drinks_per_week"]>14:
        risks.append(f"High alcohol — {p['alcohol_drinks_per_week']} drinks/week (limit: 14/week)")
        actions.append("Reduce alcohol — raises BP, triglycerides, and blood sugar")

    homa = (p["fasting_glucose"]*p["fasting_insulin"])/405
    if homa>2.5:
        risks.append(f"Insulin resistance — HOMA-IR {homa:.2f} (body not responding well to insulin)")

    if pr.get("cvd_history",{}).get("prediction",0)==1:
        risks.append("Elevated cardiovascular risk — heart attack and stroke risk above average")
        actions.append("Discuss aspirin therapy and statin use with your doctor")
        urgency = "urgent"
    else:
        positives.append("Cardiovascular risk is currently low")

    doctor = (
        "See a doctor WITHIN 2 WEEKS — high-risk conditions need immediate evaluation." if urgency=="urgent"
        else "Schedule a check-up WITHIN 1 MONTH — several modifiable risk factors found." if len(risks)>=3
        else "Visit your doctor in the next 3–6 months and share this report." if len(risks)>=1
        else "Continue with annual check-ups — your health looks good overall."
    )
    return {"risks":risks[:8],"actions":actions[:6],"positives":positives[:4],"doctor":doctor,"urgency":urgency}

# ── PAGE: OVERVIEW ────────────────────────────────────────────────────────────
def page_overview(person, predictions, advice):
    p, pr = person, predictions
    g_str    = "Male" if p["gender"]==1 else "Female"
    bmi_cat  = "Underweight" if p["bmi"]<18.5 else "Normal" if p["bmi"]<25 else "Overweight" if p["bmi"]<30 else "Obese"
    avg_sl   = round((p["sleep_hours_weekday"]*5+p["sleep_hours_weekend"]*2)/7,1)
    total_act= p["moderate_activity_min"]+p["vigorous_activity_min"]

    section_head("Patient Profile")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Age / Gender",  f"{p['age']} yrs / {g_str}")
    c2.metric("BMI",           f"{p['bmi']}", delta=bmi_cat, delta_color="off")
    c3.metric("Blood Pressure",f"{p['systolic_bp']}/{p['diastolic_bp']}", delta="mmHg", delta_color="off")
    c4.metric("HbA1c",         f"{p['hba1c']}%",
              delta="Prediabetes" if p['hba1c']>=5.7 else "Normal",
              delta_color="inverse" if p['hba1c']>=5.7 else "normal")
    c5.metric("Activity",      f"{total_act} min/wk")
    c6.metric("Sleep",         f"{avg_sl} hrs/night")

    st.markdown("---")
    section_head("All 7 Prediction Results")

    target_meta = {
        "diabetes_diagnosed"    : "🩸 Diabetes Risk",
        "cvd_history"           : "❤️ Cardiovascular",
        "hypertension_diagnosed": "💉 Hypertension",
        "metabolic_syndrome"    : "⚠️ Metabolic Syndrome",
        "diabetes_stage"        : "📊 Diabetes Stage",
        "hypertension_stage"    : "📈 HTN Stage",
        "obesity_stage"         : "⚖️ Obesity Stage",
    }

    left_targets  = list(target_meta.keys())[:4]
    right_targets = list(target_meta.keys())[4:]
    col1, col2 = st.columns(2)

    for target in left_targets:
        res  = pr.get(target,{})
        pred = res.get("prediction",0)
        conf = res.get("confidence",0)
        label= res.get("label","N/A")
        icon, rlabel, level = risk_info(target, pred)
        with col1:
            tag_cls = {"low":"risk-low","med":"risk-med","high":"risk-high"}[level]
            st.markdown(f'<span class="risk-tag {tag_cls}">● {icon} {label}</span> <span style="color:var(--text-3);font-size:12px">{target_meta[target]}</span>', unsafe_allow_html=True)
            st.progress(int(conf))
            st.caption(f"Confidence {conf}%  ·  {res.get('model_used','')}")
            st.markdown("")

    for target in right_targets:
        res  = pr.get(target,{})
        pred = res.get("prediction",0)
        conf = res.get("confidence",0)
        label= res.get("label","N/A")
        icon, rlabel, level = risk_info(target, pred)
        with col2:
            tag_cls = {"low":"risk-low","med":"risk-med","high":"risk-high"}[level]
            st.markdown(f'<span class="risk-tag {tag_cls}">● {icon} {label}</span> <span style="color:var(--text-3);font-size:12px">{target_meta[target]}</span>', unsafe_allow_html=True)
            st.progress(int(conf))
            st.caption(f"Confidence {conf}%  ·  {res.get('model_used','')}")
            st.markdown("")

    st.markdown("---")
    section_head("Quick Summary")
    n = len(advice["risks"])
    if   n==0: st.success("✅ Excellent! No major risk factors detected. Maintain your current healthy habits.")
    elif n<=2: st.warning(f"⚠️ {n} risk factor(s) identified. See individual sections for detailed guidance.")
    else:      st.error(f"🔴 {n} risk factors identified. Review each section and consult a healthcare professional.")
    st.info(f"🩺 **Doctor Recommendation:** {advice['doctor']}")

# ── PAGE: DIABETES ────────────────────────────────────────────────────────────
def page_diabetes(person, predictions, advice):
    p, pr = person, predictions
    res_d = pr.get("diabetes_diagnosed",{})
    res_s = pr.get("diabetes_stage",{})
    homa  = round((p["fasting_glucose"]*p["fasting_insulin"])/405, 2)

    st.markdown("## 🩸 Diabetes Risk Analysis")
    st.caption("Prediction using HbA1c, fasting glucose, insulin resistance index (HOMA-IR), and lifestyle factors.")
    st.markdown("---")

    section_head("Clinical Biomarkers")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("HbA1c",       f"{p['hba1c']}%",   delta="⚠ Prediabetes" if p['hba1c']>=5.7 else "✓ Normal",   delta_color="inverse" if p['hba1c']>=5.7 else "normal")
    c2.metric("Fasting Glucose",f"{p['fasting_glucose']} mg/dL", delta="⚠ Elevated" if p['fasting_glucose']>=100 else "✓ Normal", delta_color="inverse" if p['fasting_glucose']>=100 else "normal")
    c3.metric("Fasting Insulin",f"{p['fasting_insulin']} µU/mL")
    c4.metric("HOMA-IR",     f"{homa}",           delta="⚠ Resistant" if homa>2.5 else "✓ Normal",            delta_color="inverse" if homa>2.5 else "normal")

    st.markdown("---")
    section_head("ML Model Predictions")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Binary Classification — Diabetes Risk")
        pred = res_d.get("prediction",0); conf = res_d.get("confidence",0); label = res_d.get("label","N/A")
        if pred==0: st.success(f"✅ **{label}** — {conf}% confidence")
        else:       st.error(  f"🔴 **{label}** — {conf}% confidence")
        st.progress(int(conf))
        st.caption(f"Model: {res_d.get('model_used','')}  |  Training AUC: 92.4%")
        st.markdown("")
        for lbl, prob in res_d.get("probabilities",{}).items():
            st.markdown(f"**{lbl}:** {prob}%"); st.progress(int(prob))

    with col2:
        st.markdown("##### Multi-class — Diabetes Stage")
        pred = res_s.get("prediction",0); conf = res_s.get("confidence",0); label = res_s.get("label","N/A")
        if pred==0: st.success(f"🟢 **{label}** — {conf}% confidence")
        elif pred==1: st.warning(f"🟡 **{label}** — {conf}% confidence")
        else:         st.error(  f"🔴 **{label}** — {conf}% confidence")
        st.progress(int(conf))
        st.caption(f"Model: {res_s.get('model_used','')}  |  Training AUC: 98.9%")
        st.markdown("")
        for lbl, prob in res_s.get("probabilities",{}).items():
            st.markdown(f"**{lbl}:** {prob}%"); st.progress(int(prob))

    st.markdown("---")
    section_head("ADA Clinical Thresholds")
    t1,t2,t3 = st.columns(3)
    with t1:
        st.markdown("**HbA1c Ranges**")
        st.markdown("🟢 Normal — < 5.7%\n🟡 Prediabetes — 5.7–6.4%\n🔴 Diabetes — ≥ 6.5%")
        st.info(f"Your value: **{p['hba1c']}%**")
    with t2:
        st.markdown("**Fasting Glucose**")
        st.markdown("🟢 Normal — < 100 mg/dL\n🟡 Prediabetes — 100–125\n🔴 Diabetes — ≥ 126")
        st.info(f"Your value: **{p['fasting_glucose']} mg/dL**")
    with t3:
        st.markdown("**HOMA-IR**")
        st.markdown("🟢 Normal — < 1.5\n🟡 Borderline — 1.5–2.5\n🔴 Resistant — > 2.5")
        st.info(f"Your value: **{homa}**")

    st.markdown("---")
    section_head("Personalised Recommendations")
    diab_risks   = [r for r in advice["risks"]   if any(k in r.lower() for k in ["diabet","hba1c","glucose","insulin"])]
    diab_actions = [a for a in advice["actions"] if any(k in a.lower() for k in ["sugar","carb","insulin","hba1c","walk","exercise"])]
    if diab_risks:
        for r in diab_risks: st.warning(f"⚠ {r}")
    else:
        st.success("✅ No diabetes risk factors detected in your profile.")
    for i,a in enumerate(diab_actions,1): st.info(f"**Action {i}:** {a}")

# ── PAGE: CARDIOVASCULAR ──────────────────────────────────────────────────────
def page_cardiovascular(person, predictions, advice):
    p, pr = person, predictions
    res = pr.get("cvd_history",{})
    pulse  = p["systolic_bp"] - p["diastolic_bp"]
    tchdl  = round(p["total_cholesterol"] / max(p["hdl_cholesterol"],1), 2)
    ldlhdl = round(p["ldl_cholesterol"]   / max(p["hdl_cholesterol"],1), 2)

    st.markdown("## ❤️ Cardiovascular Risk Analysis")
    st.caption("Risk prediction using blood pressure, lipid panel, CRP inflammation marker, and lifestyle factors.")
    st.markdown("---")

    section_head("Clinical Biomarkers")
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Systolic BP",    f"{p['systolic_bp']} mmHg",   delta="High" if p['systolic_bp']>=130 else "Normal", delta_color="inverse" if p['systolic_bp']>=130 else "normal")
    c2.metric("Total Cholesterol",f"{p['total_cholesterol']} mg/dL", delta="High" if p['total_cholesterol']>=200 else "Normal", delta_color="inverse" if p['total_cholesterol']>=200 else "normal")
    c3.metric("LDL",            f"{p['ldl_cholesterol']} mg/dL", delta="High" if p['ldl_cholesterol']>=130 else "Normal", delta_color="inverse" if p['ldl_cholesterol']>=130 else "normal")
    c4.metric("HDL",            f"{p['hdl_cholesterol']} mg/dL", delta="Low" if p['hdl_cholesterol']<40 else "Good",   delta_color="inverse" if p['hdl_cholesterol']<40 else "normal")
    c5.metric("CRP",            f"{p['c_reactive_protein']} mg/L", delta="Elevated" if p['c_reactive_protein']>3 else "Normal", delta_color="inverse" if p['c_reactive_protein']>3 else "normal")

    st.markdown("---")
    section_head("ML Model Prediction")
    pred = res.get("prediction",0); conf = res.get("confidence",0); label = res.get("label","N/A")
    col1, col2 = st.columns(2)
    with col1:
        if pred==0: st.success(f"✅ **{label}** — {conf}% confidence")
        else:       st.error(  f"🔴 **{label}** — {conf}% confidence")
        st.progress(int(conf))
        st.caption(f"Model: {res.get('model_used','')}  |  Training AUC: 81.2%")
        st.markdown("")
        for lbl, prob in res.get("probabilities",{}).items():
            st.markdown(f"**{lbl}:** {prob}%"); st.progress(int(prob))
    with col2:
        st.metric("Pulse Pressure",  f"{pulse} mmHg",  delta="Elevated" if pulse>60 else "Normal", delta_color="inverse" if pulse>60 else "normal")
        st.markdown("")
        st.metric("Total / HDL Ratio",f"{tchdl}",      delta="High Risk" if tchdl>5 else "Normal",  delta_color="inverse" if tchdl>5 else "normal")
        st.markdown("")
        st.metric("LDL / HDL Ratio",  f"{ldlhdl}",     delta="High Risk" if ldlhdl>3.5 else "Normal",delta_color="inverse" if ldlhdl>3.5 else "normal")

    st.markdown("---")
    section_head("AHA Cholesterol Guidelines")
    t1,t2,t3 = st.columns(3)
    with t1:
        st.markdown("**LDL (Bad Cholesterol)**")
        st.markdown("🟢 Optimal — < 100 mg/dL\n🟡 Borderline — 130–159\n🔴 High — ≥ 160")
        st.info(f"Your value: **{p['ldl_cholesterol']} mg/dL**")
    with t2:
        st.markdown("**HDL (Good Cholesterol)**")
        st.markdown("🔴 Low — < 40 (men) / < 50 (women)\n🟡 Borderline — 40–59\n🟢 Optimal — ≥ 60")
        st.info(f"Your value: **{p['hdl_cholesterol']} mg/dL**")
    with t3:
        st.markdown("**Triglycerides**")
        st.markdown("🟢 Normal — < 150 mg/dL\n🟡 Borderline — 150–199\n🔴 High — ≥ 200")
        st.info(f"Your value: **{p['triglycerides']} mg/dL**")

    st.markdown("---")
    section_head("Personalised Recommendations")
    cvd_risks   = [r for r in advice["risks"]   if any(k in r.lower() for k in ["cholesterol","ldl","hdl","triglyc","cardiovasc","crp","inflam"])]
    cvd_actions = [a for a in advice["actions"] if any(k in a.lower() for k in ["sodium","fiber","hdl","fish","omega","potassium","stress","medicat"])]
    if cvd_risks:
        for r in cvd_risks: st.warning(f"⚠ {r}")
    else:
        st.success("✅ No major cardiovascular risk factors detected.")
    for i,a in enumerate(cvd_actions,1): st.info(f"**Action {i}:** {a}")

# ── PAGE: HYPERTENSION ────────────────────────────────────────────────────────
def page_hypertension(person, predictions, advice):
    p, pr = person, predictions
    res_b = pr.get("hypertension_diagnosed",{})
    res_s = pr.get("hypertension_stage",{})
    pulse = p["systolic_bp"] - p["diastolic_bp"]

    st.markdown("## 💉 Hypertension Risk Analysis")
    st.caption("Blood pressure staging using AHA 2017 guidelines with multi-class and binary predictions.")
    st.markdown("---")

    section_head("Blood Pressure Readings")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Systolic BP",  f"{p['systolic_bp']} mmHg", delta="High" if p['systolic_bp']>=130 else "Normal", delta_color="inverse" if p['systolic_bp']>=130 else "normal")
    c2.metric("Diastolic BP", f"{p['diastolic_bp']} mmHg",delta="High" if p['diastolic_bp']>=80  else "Normal",delta_color="inverse" if p['diastolic_bp']>=80  else "normal")
    c3.metric("Pulse Pressure",f"{pulse} mmHg",           delta="Elevated" if pulse>60 else "Normal",          delta_color="inverse" if pulse>60 else "normal")
    c4.metric("BP Medication", "Yes" if p['on_bp_medication'] else "No")

    st.markdown("---")
    section_head("ML Model Predictions")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Binary — Hypertension Risk")
        pred = res_b.get("prediction",0); conf = res_b.get("confidence",0); label = res_b.get("label","N/A")
        if pred==0: st.success(f"✅ **{label}** — {conf}% confidence")
        else:       st.error(  f"🔴 **{label}** — {conf}% confidence")
        st.progress(int(conf))
        st.caption(f"Model: {res_b.get('model_used','')}  |  Training AUC: 82.7%")
        st.markdown("")
        for lbl, prob in res_b.get("probabilities",{}).items():
            st.markdown(f"**{lbl}:** {prob}%"); st.progress(int(prob))
    with col2:
        st.markdown("##### Multi-class — HTN Stage")
        pred = res_s.get("prediction",0); conf = res_s.get("confidence",0); label = res_s.get("label","N/A")
        if pred==0: st.success(f"🟢 **{label}** — {conf}% confidence")
        elif pred==1: st.warning(f"🟡 **{label}** — {conf}% confidence")
        else:         st.error(  f"🔴 **{label}** — {conf}% confidence")
        st.progress(int(conf))
        st.caption(f"Model: {res_s.get('model_used','')}  |  Training AUC: 100%")
        st.markdown("")
        for lbl, prob in res_s.get("probabilities",{}).items():
            st.markdown(f"**{lbl}:** {prob}%"); st.progress(int(prob))

    st.markdown("---")
    section_head("AHA BP Staging")
    t1,t2,t3,t4 = st.columns(4)
    t1.success("**🟢 Normal**\nSystolic < 120\nDiastolic < 80")
    t2.info("**🟡 Elevated**\nSystolic 120–129\nDiastolic < 80")
    t3.warning("**🟠 Stage 1**\nSystolic 130–139\nDiastolic 80–89")
    t4.error("**🔴 Stage 2**\nSystolic ≥ 140\nDiastolic ≥ 90")

    st.markdown("---")
    section_head("Personalised Recommendations")
    htn_risks   = [r for r in advice["risks"]   if any(k in r.lower() for k in ["hypertens","blood press","bp"])]
    htn_actions = [a for a in advice["actions"] if any(k in a.lower() for k in ["sodium","potassium","stress","breath","medicat","bp"])]
    if htn_risks:
        for r in htn_risks: st.warning(f"⚠ {r}")
    else:
        st.success("✅ Blood pressure is well controlled.")
    for i,a in enumerate(htn_actions,1): st.info(f"**Action {i}:** {a}")

# ── PAGE: METABOLIC SYNDROME ──────────────────────────────────────────────────
def page_metabolic(person, predictions, advice):
    p, pr = person, predictions
    res   = pr.get("metabolic_syndrome",{})

    waist_risk = (p["waist_cm"]>102 and p["gender"]==1) or (p["waist_cm"]>88 and p["gender"]==2)
    trig_risk  = p["triglycerides"]>=150
    hdl_risk   = (p["hdl_cholesterol"]<40 and p["gender"]==1) or (p["hdl_cholesterol"]<50 and p["gender"]==2)
    bp_risk    = p["systolic_bp"]>=130 or p["diastolic_bp"]>=85 or p["on_bp_medication"]==1
    glu_risk   = p["fasting_glucose"]>=100
    met        = sum([waist_risk,trig_risk,hdl_risk,bp_risk,glu_risk])

    st.markdown("## ⚠️ Metabolic Syndrome Detection")
    st.caption("Metabolic syndrome is diagnosed when 3 or more of 5 clinical criteria are met (IDF/AHA/NHLBI).")
    st.markdown("---")

    section_head("5 Diagnostic Criteria")
    c1,c2,c3,c4,c5 = st.columns(5)
    for col, label, val, risk, unit in [
        (c1,"🦺 Waist",       f"{p['waist_cm']} cm",       waist_risk,"cm"),
        (c2,"📊 Triglycerides",f"{p['triglycerides']} mg/dL",trig_risk,""),
        (c3,"💛 HDL",         f"{p['hdl_cholesterol']} mg/dL",hdl_risk,""),
        (c4,"🩺 Blood Pressure",f"{p['systolic_bp']}/{p['diastolic_bp']}",bp_risk,""),
        (c5,"🩸 Glucose",     f"{p['fasting_glucose']} mg/dL",glu_risk,""),
    ]:
        col.metric(label, val, delta="⚠ RISK" if risk else "✓ Normal", delta_color="inverse" if risk else "normal")

    st.markdown("---")
    if   met>=3: st.error(  f"🔴 **{met}/5 criteria met — Metabolic Syndrome CONFIRMED** (threshold ≥ 3)")
    elif met==2: st.warning(f"🟡 **{met}/5 criteria met — At Risk** (one more criterion = Metabolic Syndrome)")
    else:        st.success(f"🟢 **{met}/5 criteria met — No Metabolic Syndrome**")

    st.markdown("---")
    section_head("ML Model Prediction")
    pred = res.get("prediction",0); conf = res.get("confidence",0); label = res.get("label","N/A")
    col1, col2 = st.columns(2)
    with col1:
        if pred==0: st.success(f"✅ **{label}** — {conf}% confidence")
        else:       st.error(  f"🔴 **{label}** — {conf}% confidence")
        st.progress(int(conf))
        st.caption(f"Model: {res.get('model_used','')}  |  Training AUC: 99.9%")
        st.markdown("")
        for lbl, prob in res.get("probabilities",{}).items():
            st.markdown(f"**{lbl}:** {prob}%"); st.progress(int(prob))

    st.markdown("---")
    section_head("Personalised Recommendations")
    ms_risks   = [r for r in advice["risks"]   if any(k in r.lower() for k in ["metabolic","waist","trigly","hdl","glucose","insulin"])]
    ms_actions = [a for a in advice["actions"] if any(k in a.lower() for k in ["exercise","weight","fiber","sodium","carb","sugar","omega"])]
    if ms_risks:
        for r in ms_risks: st.warning(f"⚠ {r}")
    else:
        st.success("✅ No metabolic syndrome risk factors detected.")
    for i,a in enumerate(ms_actions,1): st.info(f"**Action {i}:** {a}")

# ── PAGE: HEALTH RISK SCORE ───────────────────────────────────────────────────
def page_health_risk_score(person, predictions, advice):
    p, pr = person, predictions

    risk_scores = {
        "Diabetes Risk"      : pr.get("diabetes_diagnosed",{}).get("prediction",0)*25,
        "Cardiovascular Risk": pr.get("cvd_history",{}).get("prediction",0)*25,
        "Hypertension Risk"  : pr.get("hypertension_diagnosed",{}).get("prediction",0)*20,
        "Metabolic Syndrome" : pr.get("metabolic_syndrome",{}).get("prediction",0)*20,
        "Diabetes Stage"     : pr.get("diabetes_stage",{}).get("prediction",0)*15,
        "Hypertension Stage" : min(pr.get("hypertension_stage",{}).get("prediction",0)*10,20),
        "Obesity Stage"      : max(0,(pr.get("obesity_stage",{}).get("prediction",0)-1))*10,
    }
    if p["hba1c"]>=6.5:   risk_scores["High HbA1c"]=15
    elif p["hba1c"]>=5.7: risk_scores["Elevated HbA1c"]=8
    if p["c_reactive_protein"]>3:                            risk_scores["High CRP"]=10
    if (p["fasting_glucose"]*p["fasting_insulin"])/405>2.5: risk_scores["Insulin Resistance"]=10
    if p["smoking_status"]==1:                               risk_scores["Smoking"]=20
    if (p["sleep_hours_weekday"]*5+p["sleep_hours_weekend"]*2)/7<7: risk_scores["Poor Sleep"]=5
    if p["moderate_activity_min"]+p["vigorous_activity_min"]<150:   risk_scores["Low Activity"]=8
    if p["alcohol_drinks_per_week"]>14:                              risk_scores["High Alcohol"]=8

    total = min(sum(risk_scores.values()), 100)

    st.markdown("## 📊 Composite Health Risk Score")
    st.caption("Weighted score (0–100) derived from all 7 ML predictions and clinical biomarker values.")
    st.markdown("---")

    col1, col2 = st.columns([1,2])
    with col1:
        section_head("Overall Score")
        color   = "#34d399" if total<=25 else "#fbbf24" if total<=50 else "#fb7185"
        level   = "Low Risk" if total<=25 else "Moderate Risk" if total<=50 else "High Risk" if total<=75 else "Very High Risk"
        st.markdown(f"""
        <div class="score-ring" style="border-color:{color};color:{color};">
          <div class="score-number">{total}</div>
          <div class="score-label" style="color:{color};">/100</div>
        </div>""", unsafe_allow_html=True)
        if   total<=25: st.success( f"**{level}** — Your health profile is generally good.")
        elif total<=50: st.warning( f"**{level}** — Several areas need attention.")
        elif total<=75: st.error(   f"**{level}** — Multiple risk factors present.")
        else:           st.error(   f"**{level}** — Urgent medical attention recommended.")

    with col2:
        section_head("Score Breakdown")
        for factor, score in sorted(risk_scores.items(), key=lambda x:-x[1]):
            if score>0:
                st.markdown(f"**{factor}** — {score} pts")
                st.progress(min(score*3, 100))

    st.markdown("---")
    section_head("Complete Risk Summary")
    tab_r, tab_a, tab_p = st.tabs(["🔴 Risk Factors", "🔵 Recommended Actions", "🟢 Positive Findings"])
    with tab_r:
        if advice["risks"]:
            for i,r in enumerate(advice["risks"],1): st.markdown(f"**{i}.** ⚠ {r}")
        else:
            st.success("No major risk factors detected!")
    with tab_a:
        for i,a in enumerate(advice["actions"],1): st.markdown(f"**{i}.** 💡 {a}")
    with tab_p:
        for pos in advice["positives"]: st.markdown(f"✅ {pos}")

    st.markdown("---")
    st.info(f"🩺 **When to See a Doctor:** {advice['doctor']}")

# ── PAGE: LIFESTYLE ───────────────────────────────────────────────────────────
def page_lifestyle(person, predictions, advice):
    p = person
    total_act = p["moderate_activity_min"] + p["vigorous_activity_min"]
    avg_sl    = round((p["sleep_hours_weekday"]*5+p["sleep_hours_weekend"]*2)/7, 1)
    homa      = round((p["fasting_glucose"]*p["fasting_insulin"])/405, 2)
    smoking_map = {0:"Never smoked",1:"Current smoker",2:"Former smoker"}
    dep_cat     = "None" if p['depression_score']<5 else "Mild" if p['depression_score']<10 else "Moderate" if p['depression_score']<15 else "Moderately Severe" if p['depression_score']<20 else "Severe"

    st.markdown("## 🌿 Lifestyle Impact Analysis")
    st.caption("How your lifestyle choices affect cardiometabolic risk — based on NHANES 2021–2023 data patterns.")
    st.markdown("---")

    section_head("Physical Activity")
    c1,c2,c3 = st.columns(3)
    c1.metric("Moderate Activity",f"{p['moderate_activity_min']} min/wk")
    c2.metric("Vigorous Activity", f"{p['vigorous_activity_min']} min/wk")
    c3.metric("Total Activity",    f"{total_act} min/wk",
              delta="✓ Meets WHO target" if total_act>=150 else f"⚠ {150-total_act} min below WHO",
              delta_color="normal" if total_act>=150 else "inverse")
    act_pct = min(total_act/150*100, 100)
    st.progress(int(act_pct))
    st.caption(f"Activity score: {act_pct:.0f}% of WHO minimum (150 min/week)")

    st.markdown("---")
    section_head("Sleep")
    c1,c2,c3 = st.columns(3)
    c1.metric("Weekday Sleep",f"{p['sleep_hours_weekday']} hrs")
    c2.metric("Weekend Sleep",f"{p['sleep_hours_weekend']} hrs")
    c3.metric("Average Sleep",f"{avg_sl} hrs/night",
              delta="✓ Adequate" if avg_sl>=7 else "⚠ Below 7 hr target",
              delta_color="normal" if avg_sl>=7 else "inverse")
    st.progress(int(min(avg_sl/8*100, 100)))
    st.caption(f"Sleep score: {min(avg_sl/8*100,100):.0f}% of optimal 8 hrs/night")

    st.markdown("---")
    section_head("Smoking & Alcohol")
    c1,c2,c3 = st.columns(3)
    c1.metric("Smoking",       smoking_map.get(p["smoking_status"],"Unknown"))
    c2.metric("Cigarettes/day",f"{p['cigarettes_per_day']}")
    c3.metric("Alcohol/week",  f"{p['alcohol_drinks_per_week']} drinks",
              delta="⚠ Above limit" if p["alcohol_drinks_per_week"]>14 else "✓ Within limit",
              delta_color="inverse" if p["alcohol_drinks_per_week"]>14 else "normal")

    st.markdown("---")
    section_head("Mental Health")
    c1,c2 = st.columns(2)
    c1.metric("PHQ-9 Depression Score",f"{p['depression_score']}/27",
              delta=dep_cat, delta_color="inverse" if p['depression_score']>=10 else "normal")
    c2.metric("HOMA-IR (Insulin Resistance)",f"{homa}",
              delta="⚠ Resistant" if homa>2.5 else "✓ Normal",
              delta_color="inverse" if homa>2.5 else "normal")

    st.markdown("---")
    section_head("Lifestyle Improvement Plan")
    ls_risks   = [r for r in advice["risks"]   if any(k in r.lower() for k in ["sleep","smoking","alcohol","activity","inflam"])]
    ls_actions = [a for a in advice["actions"] if any(k in a.lower() for k in ["walk","exercise","sleep","smoking","alcohol","stress","breath","activity"])]
    if ls_risks:
        for r in ls_risks: st.warning(f"⚠ {r}")
    if ls_actions:
        for i,a in enumerate(ls_actions,1): st.info(f"**Action {i}:** {a}")
    if not ls_risks and not ls_actions:
        st.success("✅ Your lifestyle habits are excellent — keep it up!")

    st.markdown("---")
    section_head("Evidence-Based Risk Reductions")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**150 min/week exercise reduces:**")
        st.markdown("• Diabetes risk — 58% reduction\n• Cardiovascular risk — 35%\n• Hypertension risk — 25%\n• Depression — 30%")
    with c2:
        st.markdown("**Losing 5–10% body weight reduces:**")
        st.markdown("• Diabetes risk — 50–60%\n• BP by 5–10 mmHg\n• Triglycerides — 20%\n• Metabolic syndrome reversal — 40%")

# ── PATIENT INTAKE FORM ───────────────────────────────────────────────────────
def patient_intake():
    st.markdown("---")
    section_head("Patient Intake Form")

    with st.form("intake_form"):
        left, right = st.columns([1.05, 1])

        with left:
            st.markdown("#### Demographics")
            age    = st.number_input("Age (years)", 18, 80, 52, step=1)
            gender = st.selectbox("Gender", [("Male",1),("Female",2)], format_func=lambda x:x[0])
            income = st.number_input("Income / Poverty Ratio", 0.0, 5.0, 3.5, step=0.1)
            st.caption("1.0 = at poverty line, 5.0 = 5× above poverty line.")

            st.markdown("#### Body Measurements")
            weight = st.number_input("Weight (kg)", 30.0, 300.0, 95.0, step=0.5)
            height = st.number_input("Height (cm)", 100.0, 220.0, 175.0, step=0.5)
            bmi    = round(weight / ((height/100)**2), 1)
            bmi_cat= "Underweight" if bmi<18.5 else "Normal" if bmi<25 else "Overweight" if bmi<30 else "Obese"
            st.markdown(f'<div class="inline-bmi">📊 BMI = <strong>{bmi}</strong> &nbsp;·&nbsp; {bmi_cat}</div>', unsafe_allow_html=True)
            waist  = st.number_input("Waist circumference (cm)", 40.0, 200.0, 108.0, step=0.5)

        with right:
            st.markdown("#### Blood Pressure")
            sbp    = st.number_input("Systolic BP (mmHg)", 70, 250, 138)
            dbp    = st.number_input("Diastolic BP (mmHg)", 30, 150, 88)
            bp_med = st.selectbox("On BP Medication?", [("No",0),("Yes",1)], format_func=lambda x:x[0])

            with st.expander("Lab Values", expanded=True):
                hba1c   = st.number_input("HbA1c (%)",               3.0, 20.0, 6.3, step=0.1)
                glucose = st.number_input("Fasting Glucose (mg/dL)", 40, 600, 112)
                insulin = st.number_input("Fasting Insulin (µU/mL)", 1.0, 300.0, 18.0, step=0.5)
                tchol   = st.number_input("Total Cholesterol (mg/dL)",80, 600, 215)
                hdl     = st.number_input("HDL Cholesterol (mg/dL)",  10, 150, 42)
                ldl     = st.number_input("LDL Cholesterol (mg/dL)",  20, 500, 135)
                trig    = st.number_input("Triglycerides (mg/dL)",    20, 1000, 185)
                crp     = st.number_input("C-Reactive Protein (mg/L)",0.1, 50.0, 3.2, step=0.1)

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Lifestyle")
            smoking = st.selectbox("Smoking Status", [("Never",0),("Current",1),("Former",2)], format_func=lambda x:x[0])
            cigs    = st.number_input("Cigarettes/day",               0, 100, 0)
            mod_act = st.number_input("Moderate activity (min/week)", 0, 3000, 60)
            vig_act = st.number_input("Vigorous activity (min/week)", 0, 3000, 0)
            alcohol = st.number_input("Alcohol drinks/week",          0, 50, 5)
        with c2:
            st.markdown("#### Sleep & Mental Health")
            sleep_w = st.number_input("Weekday sleep (hrs/night)", 2.0, 16.0, 6.5, step=0.5)
            sleep_e = st.number_input("Weekend sleep (hrs/night)", 2.0, 16.0, 8.0, step=0.5)
            depress = st.number_input("PHQ-9 Depression Score (0–27)", 0, 27, 4, step=1)
            st.caption("PHQ-9 scale: 0–4 minimal, 5–9 mild, 10–14 moderate, 15–19 moderately severe, 20–27 severe.")

        run = st.form_submit_button("⚕ Run Health Analysis", use_container_width=True)

    person = {
        "age":age,"gender":gender[1],"race":3,"education":4,
        "marital_status":1,"income_poverty_ratio":income,
        "weight_kg":weight,"height_cm":height,"bmi":bmi,"waist_cm":waist,
        "systolic_bp":sbp,"diastolic_bp":dbp,
        "hba1c":hba1c,"fasting_glucose":glucose,"fasting_insulin":insulin,
        "total_cholesterol":tchol,"hdl_cholesterol":hdl,
        "triglycerides":trig,"ldl_cholesterol":ldl,"c_reactive_protein":crp,
        "smoking_status":smoking[1],"cigarettes_per_day":cigs,
        "moderate_activity_min":mod_act,"vigorous_activity_min":vig_act,
        "alcohol_drinks_per_week":alcohol,"fast_food_times_per_week":0,
        "depression_score":depress,"sleep_hours_weekday":sleep_w,
        "sleep_hours_weekend":sleep_e,"on_bp_medication":bp_med[1],
    }
    return person, run

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    models = load_models()

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero">
      <div class="hero-left">
        <div class="hero-eyebrow">NHANES 2021–2023  ·  Clinical AI</div>
        <div class="hero-title">HealthAI Clinical Risk Studio</div>
        <div class="hero-sub">
          Real-time cardiometabolic risk assessment across 7 conditions with personalised clinical guidance — powered by ensemble machine learning trained on 6,174 patient records.
        </div>
        <div class="hero-pills">
          <span class="pill">7 ML Models</span>
          <span class="pill g">6,174 Records</span>
          <span class="pill a">Evidence-Based Advice</span>
          <span class="pill">NHANES 2021–2023</span>
        </div>
      </div>
      <div class="hero-stats">
        <div class="hstat"><div class="hstat-label">Dataset</div><div class="hstat-value">NHANES</div></div>
        <div class="hstat"><div class="hstat-label">Models</div><div class="hstat-value">21</div></div>
        <div class="hstat"><div class="hstat-label">Targets</div><div class="hstat-value">7</div></div>
        <div class="hstat"><div class="hstat-label">Best AUC</div><div class="hstat-value">99.9%</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    person, run_clicked = patient_intake()

    if run_clicked or st.session_state.get("has_results", False):
        if run_clicked:
            with st.spinner("Running ensemble models..."):
                predictions = run_all_predictions(person, models)
                advice      = generate_advice(person, predictions)
            st.session_state.update({"has_results":True,"predictions":predictions,"advice":advice,"person":person})
            st.success("✅ Analysis complete — navigate the report sections below.")
            st.markdown("")

        predictions = st.session_state["predictions"]
        advice      = st.session_state["advice"]
        person      = st.session_state["person"]

        st.markdown("---")
        section_head("Report Navigation")

        section = st.radio(
            "Report",
            ["📋 Overview","🩸 Diabetes","❤️ Cardiovascular","💉 Hypertension",
             "⚠️ Metabolic Syndrome","📊 Health Risk Score","🌿 Lifestyle"],
            horizontal=True, label_visibility="collapsed", key="nav"
        )

        st.markdown("")

        page_map = {
            "📋 Overview"         : page_overview,
            "🩸 Diabetes"         : page_diabetes,
            "❤️ Cardiovascular"   : page_cardiovascular,
            "💉 Hypertension"     : page_hypertension,
            "⚠️ Metabolic Syndrome": page_metabolic,
            "📊 Health Risk Score" : page_health_risk_score,
            "🌿 Lifestyle"        : page_lifestyle,
        }
        page_map[section](person, predictions, advice)

        st.markdown("---")
        st.caption("⚕ Built on NHANES 2021–2023 (CDC) · For educational & research purposes only · Not medical advice · Consult a qualified healthcare professional for clinical decisions.")

    else:
        st.markdown("")
        section_head("Available Prediction Models")
        cols = st.columns(4)
        for i, (icon, name, algo, auc) in enumerate([
            ("🩸","Diabetes Risk",    "Random Forest",       "92.4% AUC"),
            ("❤️","Cardiovascular",   "Logistic Regression", "81.2% AUC"),
            ("💉","Hypertension Risk","Logistic Regression", "82.7% AUC"),
            ("⚠️","Metabolic Syndrome","XGBoost",            "99.9% AUC"),
            ("📊","Diabetes Stage",   "XGBoost",             "98.9% AUC"),
            ("📈","HTN Stage",        "Random Forest",       "100% AUC"),
            ("⚖️","Obesity Stage",    "Random Forest",       "100% AUC"),
        ]):
            with cols[i % 4]:
                st.metric(f"{icon} {name}", auc, delta=algo, delta_color="off")
                st.markdown("")

        st.markdown("")
        c1,c2,c3 = st.columns(3)
        c1.info("**🔬 7 Predictions**\n\nDiabetes, CVD, Hypertension, Metabolic Syndrome, Obesity stages")
        c2.info("**📊 Clinical Analysis**\n\nProbability scores, confidence levels, ADA/AHA/WHO thresholds")
        c3.info("**💡 Personalised Advice**\n\nActionable recommendations based on your specific clinical profile")

if __name__ == "__main__":
    main()
