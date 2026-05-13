"""
NHANES PROJECT - STEP 5
AI Health Advice Generator — No API needed
Uses smart rule-based engine to generate personalized health advice
based on ML predictions and clinical values
"""

import pickle
import numpy as np
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# ── CONFIG ────────────────────────────────────────────────────────────────────
MODELS_DIR  = "models"
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

# ── MODEL FILES ───────────────────────────────────────────────────────────────
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
    "diabetes_diagnosed"    : {0: "No Diabetes",           1: "Diabetes Likely"},
    "cvd_history"           : {0: "Low CVD Risk",          1: "High CVD Risk"},
    "hypertension_diagnosed": {0: "No Hypertension",       1: "Hypertension Likely"},
    "metabolic_syndrome"    : {0: "No Metabolic Syndrome", 1: "Metabolic Syndrome Detected"},
    "diabetes_stage"        : {0: "Normal",    1: "Prediabetes",          2: "Diabetes"},
    "hypertension_stage"    : {0: "Normal BP", 1: "Elevated BP",          2: "Stage 1 Hypertension", 3: "Stage 2 Hypertension"},
    "obesity_stage"         : {0: "Underweight", 1: "Normal Weight",      2: "Overweight", 3: "Obese"},
}

RISK_NAMES = {
    "diabetes_diagnosed"    : "Diabetes Risk",
    "cvd_history"           : "Cardiovascular Risk",
    "hypertension_diagnosed": "Hypertension Risk",
    "metabolic_syndrome"    : "Metabolic Syndrome",
    "diabetes_stage"        : "Diabetes Stage",
    "hypertension_stage"    : "Hypertension Stage",
    "obesity_stage"         : "Obesity Stage",
}


# ── LOAD ALL MODELS ───────────────────────────────────────────────────────────
def load_all_models():
    print("=" * 65)
    print("  NHANES HEALTH AI — PERSONALIZED HEALTH REPORT")
    print("=" * 65)
    print("\n[1/4] Loading saved ML models...")

    models = {}
    for target, filename in MODEL_FILES.items():
        path = os.path.join(MODELS_DIR, filename)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                models[target] = pickle.load(f)
            print(f"  ✓ {RISK_NAMES[target]:<30} ({models[target]['model_name']})")
        else:
            print(f"  ✗ MISSING: {filename}")

    print(f"\n  {len(models)}/7 models loaded")
    return models


# ── PERSON PROFILE ────────────────────────────────────────────────────────────
def get_person_profile():
    """Edit these values to test different people."""
    return {
        "age"                    : 52,
        "gender"                 : 1,
        "race"                   : 3,
        "education"              : 4,
        "marital_status"         : 1,
        "income_poverty_ratio"   : 3.5,
        "weight_kg"              : 95.0,
        "height_cm"              : 175.0,
        "bmi"                    : 31.0,
        "waist_cm"               : 108.0,
        "systolic_bp"            : 138.0,
        "diastolic_bp"           : 88.0,
        "hba1c"                  : 6.3,
        "fasting_glucose"        : 112.0,
        "fasting_insulin"        : 18.0,
        "total_cholesterol"      : 215.0,
        "hdl_cholesterol"        : 42.0,
        "triglycerides"          : 185.0,
        "ldl_cholesterol"        : 135.0,
        "c_reactive_protein"     : 3.2,
        "smoking_status"         : 0,
        "cigarettes_per_day"     : 0,
        "moderate_activity_min"  : 60,
        "vigorous_activity_min"  : 0,
        "alcohol_drinks_per_week": 5,
        "fast_food_times_per_week": 0,
        "depression_score"       : 4,
        "sleep_hours_weekday"    : 6.5,
        "sleep_hours_weekend"    : 8.0,
        "on_bp_medication"       : 0,
    }


# ── PREPARE FEATURES ──────────────────────────────────────────────────────────
def prepare_features(person, model_obj):
    p = person.copy()

    p['total_hdl_ratio']    = p['total_cholesterol'] / max(p['hdl_cholesterol'], 1)
    p['ldl_hdl_ratio']      = p['ldl_cholesterol'] / max(p['hdl_cholesterol'], 1)
    p['pulse_pressure']     = p['systolic_bp'] - p['diastolic_bp']
    p['homa_ir']            = (p['fasting_glucose'] * p['fasting_insulin']) / 405
    p['waist_height_ratio'] = p['waist_cm'] / p['height_cm']
    p['avg_sleep_hours']    = (p['sleep_hours_weekday'] * 5 + p['sleep_hours_weekend'] * 2) / 7
    p['total_activity_min'] = p['moderate_activity_min'] + p['vigorous_activity_min']
    p['smoking_intensity']  = p['cigarettes_per_day']

    bmi = p['bmi']
    bmi_cat = 'Underweight' if bmi < 18.5 else 'Normal' if bmi < 25 else 'Overweight' if bmi < 30 else 'Obese'
    p['bmi_category_Normal']      = 1 if bmi_cat == 'Normal'     else 0
    p['bmi_category_Overweight']  = 1 if bmi_cat == 'Overweight' else 0
    p['bmi_category_Obese']       = 1 if bmi_cat == 'Obese'      else 0
    p['bmi_category_Unknown']     = 0

    age = p['age']
    age_g = '18-34' if age < 35 else '35-49' if age < 50 else '50-64' if age < 65 else '65+'
    p['age_group_35-49']   = 1 if age_g == '35-49' else 0
    p['age_group_50-64']   = 1 if age_g == '50-64' else 0
    p['age_group_65+']     = 1 if age_g == '65+'   else 0
    p['age_group_Unknown'] = 0

    act = p['total_activity_min']
    act_l = 'Sedentary' if act == 0 else 'Low' if act < 150 else 'Moderate' if act < 300 else 'High'
    p['activity_level_Low']      = 1 if act_l == 'Low'      else 0
    p['activity_level_Moderate'] = 1 if act_l == 'Moderate' else 0
    p['activity_level_High']     = 1 if act_l == 'High'     else 0
    p['activity_level_Unknown']  = 0

    p['smoking_status_2'] = 1 if p['smoking_status'] == 2 else 0

    ds = p['depression_score']
    dep = 'None' if ds < 5 else 'Mild' if ds < 10 else 'Moderate' if ds < 15 else 'Moderately Severe' if ds < 20 else 'Severe'
    p['depression_category_Mild']              = 1 if dep == 'Mild'              else 0
    p['depression_category_Moderate']          = 1 if dep == 'Moderate'          else 0
    p['depression_category_Moderately Severe'] = 1 if dep == 'Moderately Severe' else 0
    p['depression_category_Severe']            = 1 if dep == 'Severe'            else 0

    p['gender_2'] = 1 if p['gender'] == 2 else 0

    race = p['race']
    for r in [2, 3, 4, 6]:
        p[f'race_{r}'] = 1 if race == r else 0

    edu = p['education']
    for e in [2, 3, 4, 5]:
        p[f'education_{e}'] = 1 if edu == e else 0

    mar = p['marital_status']
    p['marital_status_2'] = 1 if mar == 2 else 0
    p['marital_status_3'] = 1 if mar == 3 else 0

    expected_features = model_obj['features']
    row = {feat: p.get(feat, 0) for feat in expected_features}
    return pd.DataFrame([row])[expected_features]


# ── RUN PREDICTIONS ───────────────────────────────────────────────────────────
def run_predictions(person, models):
    print("\n[2/4] Running ML predictions...")

    results = {}
    for target, model_obj in models.items():
        try:
            X      = prepare_features(person, model_obj)
            model  = model_obj['model']
            scaler = model_obj['scaler']
            X_in   = scaler.transform(X) if scaler else X.values

            pred  = model.predict(X_in)[0]
            prob  = model.predict_proba(X_in)[0]
            label = LABEL_MAPS[target].get(int(pred), str(pred))
            conf  = round(float(max(prob)) * 100, 1)

            results[target] = {
                "prediction"   : int(pred),
                "label"        : label,
                "confidence"   : conf,
                "probabilities": {
                    LABEL_MAPS[target].get(i, str(i)): round(float(p) * 100, 1)
                    for i, p in enumerate(prob)
                },
                "model_used"   : model_obj['model_name'],
                "risk_name"    : RISK_NAMES[target],
            }

            icon = "✓" if int(pred) == 0 else "!"
            print(f"  {icon} {RISK_NAMES[target]:<30} {label:<28} ({conf}%)")

        except Exception as e:
            print(f"  ✗ {target}: {e}")
            results[target] = {"label": "Error", "prediction": -1, "confidence": 0,
                               "probabilities": {}, "model_used": "", "risk_name": RISK_NAMES[target]}

    return results


# ── SMART RULE-BASED ADVICE ENGINE ────────────────────────────────────────────
def generate_smart_advice(person, predictions):
    """
    Generate personalized health advice based on clinical values
    and ML predictions using medical guidelines.
    """
    p  = person
    pr = predictions

    gender_str = "Male" if p['gender'] == 1 else "Female"
    bmi        = p['bmi']
    bmi_cat    = 'Underweight' if bmi < 18.5 else 'Normal' if bmi < 25 else 'Overweight' if bmi < 30 else 'Obese'
    avg_sleep  = round((p['sleep_hours_weekday']*5 + p['sleep_hours_weekend']*2) / 7, 1)
    homa_ir    = round((p['fasting_glucose'] * p['fasting_insulin']) / 405, 2)

    # ── COLLECT RISK FLAGS ────────────────────────────────────────────────────
    risks   = []
    positives = []
    actions   = []
    urgency   = "routine"

    # Diabetes
    ds = pr.get('diabetes_stage', {}).get('prediction', 0)
    if ds == 2:
        risks.append(f"Diabetes confirmed (HbA1c: {p['hba1c']}%, Glucose: {p['fasting_glucose']} mg/dL)")
        actions.append("Monitor blood sugar daily — target fasting glucose below 126 mg/dL and HbA1c below 6.5%")
        actions.append("Follow a low-glycemic diet: reduce white rice, bread, sugary drinks — replace with whole grains, vegetables, legumes")
        urgency = "urgent"
    elif ds == 1:
        risks.append(f"Prediabetes detected (HbA1c: {p['hba1c']}% — normal is below 5.7%)")
        actions.append("Reduce sugar and refined carbohydrates — target HbA1c below 5.7% within 6 months")
        actions.append("Walk 30 minutes daily — even light exercise reduces insulin resistance significantly")
    else:
        positives.append(f"Blood sugar is in the normal range (HbA1c: {p['hba1c']}%, Glucose: {p['fasting_glucose']} mg/dL)")

    # Blood pressure
    hs = pr.get('hypertension_stage', {}).get('prediction', 0)
    sbp = p['systolic_bp']
    dbp = p['diastolic_bp']
    if hs == 3:
        risks.append(f"Stage 2 Hypertension (BP: {sbp}/{dbp} mmHg — target is below 120/80)")
        actions.append(f"See a doctor immediately — BP of {sbp}/{dbp} requires medication evaluation")
        urgency = "urgent"
    elif hs == 2:
        risks.append(f"Stage 1 Hypertension (BP: {sbp}/{dbp} mmHg — target is below 130/80)")
        actions.append(f"Reduce sodium intake to under 2,300 mg/day — avoid processed foods, canned soups, fast food")
        actions.append("Practice daily stress reduction: 10 minutes of deep breathing or meditation can lower BP by 5-8 mmHg")
    elif hs == 1:
        risks.append(f"Elevated blood pressure (BP: {sbp}/{dbp} mmHg) — early intervention needed")
        actions.append("Increase potassium-rich foods: bananas, spinach, sweet potatoes help lower blood pressure naturally")
    else:
        positives.append(f"Blood pressure is normal ({sbp}/{dbp} mmHg)")

    # Cholesterol
    if p['hdl_cholesterol'] < 40:
        risks.append(f"Low HDL (good) cholesterol: {p['hdl_cholesterol']} mg/dL — target is above 40 for men, 50 for women")
        actions.append("Increase HDL naturally: eat fatty fish (salmon, mackerel) twice a week, add olive oil, nuts, and avocado")
    elif p['hdl_cholesterol'] >= 60:
        positives.append(f"HDL (good) cholesterol is excellent ({p['hdl_cholesterol']} mg/dL)")

    if p['triglycerides'] >= 200:
        risks.append(f"High triglycerides: {p['triglycerides']} mg/dL — target is below 150 mg/dL")
        actions.append("Reduce triglycerides: avoid alcohol, sugary drinks, and refined carbs — they directly raise triglyceride levels")
    elif p['triglycerides'] < 100:
        positives.append(f"Triglycerides are excellent ({p['triglycerides']} mg/dL)")

    if p['ldl_cholesterol'] >= 130:
        risks.append(f"Elevated LDL (bad) cholesterol: {p['ldl_cholesterol']} mg/dL — target is below 100 mg/dL")
        actions.append("Lower LDL: increase soluble fiber (oats, lentils, apples) — aim for 25-30g of fiber per day")

    # Obesity / BMI
    obs = pr.get('obesity_stage', {}).get('prediction', 0)
    if obs == 3:
        risks.append(f"Obesity (BMI: {bmi}) — increases risk for diabetes, heart disease, and hypertension")
        actions.append(f"Target a weight loss of 5-10% ({round(p['weight_kg']*0.05,1)}-{round(p['weight_kg']*0.10,1)} kg) — even small reductions improve all health markers")
    elif obs == 2:
        risks.append(f"Overweight (BMI: {bmi}) — losing 5-10% of body weight reduces disease risk significantly")
    elif obs == 1:
        positives.append(f"Body weight is in the normal range (BMI: {bmi})")

    # Metabolic syndrome
    ms = pr.get('metabolic_syndrome', {}).get('prediction', 0)
    if ms == 1:
        risks.append("Metabolic syndrome detected — combination of high waist, BP, glucose, and cholesterol issues")
        actions.append("Address metabolic syndrome: the most effective intervention is 30 minutes of moderate exercise 5 days a week — this alone can reverse metabolic syndrome in 6-12 months")

    # CVD
    cvd = pr.get('cvd_history', {}).get('prediction', 0)
    if cvd == 1:
        risks.append("Elevated cardiovascular disease risk — heart attack and stroke risk is higher than average")
        actions.append("Take cardiovascular risk seriously: discuss aspirin therapy and statin use with your doctor")
        urgency = "urgent"
    else:
        positives.append("Cardiovascular risk is currently low based on your profile")

    # Inflammation
    if p['c_reactive_protein'] > 3.0:
        risks.append(f"Elevated C-reactive protein ({p['c_reactive_protein']} mg/L) — indicates systemic inflammation")
        actions.append("Reduce inflammation: add anti-inflammatory foods — turmeric, berries, leafy greens, omega-3 fatty acids")

    # Physical activity
    total_act = p['moderate_activity_min'] + p['vigorous_activity_min']
    if total_act < 150:
        actions.append(f"You currently do {total_act} minutes of activity per week — aim for at least 150 minutes of moderate activity (WHO guideline)")
    else:
        positives.append(f"Physical activity level is good ({total_act} minutes per week)")

    # Sleep
    if avg_sleep < 7:
        risks.append(f"Insufficient sleep ({avg_sleep} hours/night) — poor sleep worsens blood sugar, blood pressure, and weight")
        actions.append(f"Improve sleep to 7-9 hours per night — set a consistent bedtime, avoid screens 1 hour before bed")
    elif avg_sleep >= 7:
        positives.append(f"Sleep duration is adequate ({avg_sleep} hours/night)")

    # Smoking
    if p['smoking_status'] == 1:
        risks.append("Current smoker — smoking doubles cardiovascular risk and worsens every other condition")
        actions.append("Quitting smoking is the single most impactful health change you can make — seek cessation support")
        urgency = "urgent"
    else:
        positives.append("Non-smoker — this significantly reduces your cardiovascular and cancer risk")

    # Alcohol
    if p['alcohol_drinks_per_week'] > 14:
        risks.append(f"High alcohol consumption ({p['alcohol_drinks_per_week']} drinks/week) — limit to 14/week for men, 7/week for women")
        actions.append(f"Reduce alcohol to under 14 drinks per week — alcohol raises blood pressure, triglycerides, and blood sugar")

    # HOMA-IR
    if homa_ir > 2.5:
        risks.append(f"Insulin resistance detected (HOMA-IR: {homa_ir}) — your body is not responding well to insulin")

    # Urgency
    if urgency == "urgent":
        doctor_advice = "See a doctor WITHIN 2 WEEKS — your results show multiple high-risk conditions that need medical evaluation."
    elif len(risks) >= 3:
        doctor_advice = "Schedule a doctor visit WITHIN 1 MONTH — you have several modifiable risk factors that benefit from professional guidance."
    elif len(risks) >= 1:
        doctor_advice = "Visit your doctor for a routine check-up in the next 3-6 months and share these results."
    else:
        doctor_advice = "Continue with annual check-ups — your health markers look good overall."

    # ── BUILD REPORT TEXT ─────────────────────────────────────────────────────
    # Overall status
    high_risk_count = sum(1 for t in ['diabetes_stage', 'hypertension_stage', 'obesity_stage', 'metabolic_syndrome']
                          if predictions.get(t, {}).get('prediction', 0) > 0)

    if high_risk_count == 0:
        summary_line = f"Your overall health profile looks good with no major risk conditions detected."
    elif high_risk_count <= 2:
        summary_line = f"Your health profile shows {high_risk_count} area(s) of concern that can be addressed with lifestyle changes."
    else:
        summary_line = f"Your health profile shows {high_risk_count} significant risk areas that require attention and action."

    advice = f"""
1. HEALTH SUMMARY
   {summary_line}
   As a {p['age']}-year-old {gender_str} with BMI {bmi} ({bmi_cat}), your most important
   focus areas are: {', '.join([r.split('(')[0].strip() for r in risks[:3]]) if risks else 'maintaining your current healthy habits'}.

2. KEY RISK FACTORS IDENTIFIED ({len(risks)} found)
"""
    if risks:
        for i, r in enumerate(risks, 1):
            advice += f"   {i}. {r}\n"
    else:
        advice += "   No significant risk factors detected — keep up the good work!\n"

    advice += f"""
3. PREDICTIONS EXPLAINED
   • Diabetes Stage: {pr.get('diabetes_stage',{}).get('label','N/A')} — {'HbA1c and glucose suggest prediabetes; reversible with diet and exercise' if pr.get('diabetes_stage',{}).get('prediction',0)==1 else 'blood sugar levels are within acceptable range' if pr.get('diabetes_stage',{}).get('prediction',0)==0 else 'diabetes confirmed; requires medical management'}
   • Hypertension Stage: {pr.get('hypertension_stage',{}).get('label','N/A')} — {'blood pressure readings are elevated and require monitoring and lifestyle changes' if pr.get('hypertension_stage',{}).get('prediction',0)>0 else 'blood pressure is well controlled'}
   • Obesity Stage: {pr.get('obesity_stage',{}).get('label','N/A')} — {'excess body weight is contributing to metabolic and cardiovascular risks' if pr.get('obesity_stage',{}).get('prediction',0)>=2 else 'body weight is healthy'}
   • Metabolic Syndrome: {pr.get('metabolic_syndrome',{}).get('label','N/A')} — {'multiple metabolic risk factors are present simultaneously' if pr.get('metabolic_syndrome',{}).get('prediction',0)==1 else 'no metabolic syndrome pattern detected'}
   • Cardiovascular Risk: {pr.get('cvd_history',{}).get('label','N/A')} — {'heart disease risk is elevated; preventive action recommended' if pr.get('cvd_history',{}).get('prediction',0)==1 else 'cardiovascular risk is low based on current data'}

4. RECOMMENDED ACTIONS (priority order)
"""
    # Limit to top 6 actions
    top_actions = actions[:6]
    if not top_actions:
        top_actions = ["Maintain your current healthy lifestyle",
                       "Continue regular exercise of 150+ minutes per week",
                       "Keep up a balanced diet rich in vegetables and whole grains"]

    for i, a in enumerate(top_actions, 1):
        advice += f"   {i}. {a}\n"

    advice += f"""
5. POSITIVE FINDINGS
"""
    if positives:
        for pos in positives[:4]:
            advice += f"   + {pos}\n"
    else:
        advice += "   + No smoking habit detected\n   + You are engaging with your health proactively\n"

    advice += f"""
6. WHEN TO SEE A DOCTOR
   {doctor_advice}
   When you go, bring this report and ask your doctor about:
   {'- HbA1c management and diabetes prevention plan' if pr.get('diabetes_stage',{}).get('prediction',0)>=1 else ''}
   {'- Blood pressure management options' if pr.get('hypertension_stage',{}).get('prediction',0)>=2 else ''}
   {'- Cholesterol panel and lipid management' if p['ldl_cholesterol'] >= 130 or p['hdl_cholesterol'] < 40 else ''}
   - Annual blood work: CBC, lipid panel, HbA1c, kidney function
"""

    return advice.strip()


# ── PRINT AND SAVE REPORT ─────────────────────────────────────────────────────
def save_report(person, predictions, advice):
    print("\n[4/4] Generating and saving health report...")

    gender_str = "Male" if person['gender'] == 1 else "Female"
    bmi        = person['bmi']
    bmi_cat    = 'Underweight' if bmi < 18.5 else 'Normal' if bmi < 25 else 'Overweight' if bmi < 30 else 'Obese'
    avg_sleep  = round((person['sleep_hours_weekday']*5 + person['sleep_hours_weekend']*2) / 7, 1)

    report = f"""
{'='*65}
  NHANES HEALTH AI — PERSONALIZED HEALTH REPORT
{'='*65}

  Patient : {gender_str}, Age {person['age']}
  BMI     : {bmi} ({bmi_cat})
  BP      : {person['systolic_bp']}/{person['diastolic_bp']} mmHg
  HbA1c   : {person['hba1c']}%  |  Glucose: {person['fasting_glucose']} mg/dL
  Sleep   : {avg_sleep} hrs/night  |  Activity: {person['moderate_activity_min'] + person['vigorous_activity_min']} min/week

{'─'*65}
  ML PREDICTION RESULTS (7 models)
{'─'*65}
"""
    for target, result in predictions.items():
        icon  = "✓" if result.get('prediction', -1) == 0 else "!"
        label = result.get('label', 'N/A')
        conf  = result.get('confidence', 0)
        name  = result.get('risk_name', target)
        model = result.get('model_used', '')
        report += f"  {icon}  {name:<30} {label:<28} {conf:>5.1f}%\n"
        report += f"      └─ Model: {model}\n"

    report += f"""
{'─'*65}
  PROBABILITY BREAKDOWN
{'─'*65}
"""
    for target, result in predictions.items():
        report += f"\n  {result.get('risk_name', target)}:\n"
        for label, prob in result.get('probabilities', {}).items():
            bar = "█" * int(prob / 5)
            report += f"    {label:<30} {prob:>5.1f}%  {bar}\n"

    report += f"""
{'─'*65}
  AI-GENERATED HEALTH ADVICE
{'─'*65}
{advice}

{'─'*65}
  DISCLAIMER
{'─'*65}
  This report is generated by ML models trained on NHANES 2021-2023 data
  and a rule-based clinical advice engine. It is for educational purposes
  only and does NOT constitute medical advice. Please consult a qualified
  healthcare professional for all medical decisions.
{'='*65}
"""

    # Print to terminal
    print(report)

    # Save to file
    path = os.path.join(REPORTS_DIR, f"health_report_age{person['age']}.txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"  ✓ Report saved → {path}")
    print(f"\n{'='*65}")
    print(f"  STEP 5 COMPLETE — PROJECT PIPELINE DONE!")
    print(f"{'='*65}\n")


# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    models      = load_all_models()
    person      = get_person_profile()

    print(f"\n  Patient: Age {person['age']}, "
          f"{'Male' if person['gender']==1 else 'Female'}, "
          f"BMI {person['bmi']}, "
          f"BP {person['systolic_bp']}/{person['diastolic_bp']}")

    predictions = run_predictions(person, models)
    print("\n[3/4] Generating personalized health advice...")
    advice      = generate_smart_advice(person, predictions)
    save_report(person, predictions, advice)


if __name__ == "__main__":
    main()
