-- ============================================================================
-- NHANES PROJECT - STEP 2 FINAL
-- COMPLETE DATA CLEANING - ALL SPECIAL CODES REPLACED WITH NULL
-- Based on deep validation of all 19 XPT files
-- ============================================================================
-- NHANES Special Codes (CDC Documentation):
--   7, 77, 777, 7777    = Refused to answer
--   9, 99, 999, 9999    = Don't know / Couldn't obtain
--   .                   = Missing / Not applicable
-- ============================================================================

SET sql_mode = '';
SET SESSION group_concat_max_len = 1000000;

USE nhanes_project;

DROP TABLE IF EXISTS nhanes_master;
DROP TABLE IF EXISTS nhanes_cleaned;
DROP TABLE IF EXISTS nhanes_final;

-- ============================================================================
-- STEP 2A: MERGE ALL TABLES + CLEAN SPECIAL CODES
-- ============================================================================

CREATE TABLE nhanes_master AS
SELECT 
    d.SEQN,
    
    -- ========== DEMOGRAPHICS (CLEAN SPECIAL CODES) ==========
    d.RIDSTATR AS exam_status,
    CASE WHEN d.RIAGENDR IN (7, 9) THEN NULL ELSE d.RIAGENDR END AS gender,
    CASE WHEN d.RIDAGEYR IN (7, 9, 77, 99) THEN NULL ELSE d.RIDAGEYR END AS age,
    CASE WHEN d.RIDRETH3 IN (7, 9) THEN NULL ELSE d.RIDRETH3 END AS race,
    CASE WHEN d.DMDEDUC2 IN (7, 9, 77, 99) THEN NULL ELSE d.DMDEDUC2 END AS education,
    CASE WHEN d.DMDMARTZ IN (7, 9, 77, 99) THEN NULL ELSE d.DMDMARTZ END AS marital_status,
    d.INDFMPIR AS income_poverty_ratio,
    d.RIDEXPRG AS pregnancy_status,
    
    -- ========== BODY MEASUREMENTS (CLEAN SPECIAL CODES) ==========
    CASE WHEN bmx.BMXWT IN (7, 9, 77, 99) THEN NULL ELSE bmx.BMXWT END AS weight_kg,
    CASE WHEN bmx.BMXHT IN (7, 9, 77, 99) THEN NULL ELSE bmx.BMXHT END AS height_cm,
    bmx.BMXBMI AS bmi,  -- BMI is calculated, no special codes
    CASE WHEN bmx.BMXWAIST IN (7, 9, 77, 99) THEN NULL ELSE bmx.BMXWAIST END AS waist_cm,
    
    -- ========== BLOOD PRESSURE (CLEAN SPECIAL CODES) ==========
    CASE WHEN bp.BPXOSY1 IN (7, 9, 77, 99) THEN NULL ELSE bp.BPXOSY1 END AS systolic_bp_1,
    CASE WHEN bp.BPXODI1 IN (7, 9, 77, 99) THEN NULL ELSE bp.BPXODI1 END AS diastolic_bp_1,
    CASE WHEN bp.BPXOSY2 IN (7, 9, 77, 99) THEN NULL ELSE bp.BPXOSY2 END AS systolic_bp_2,
    CASE WHEN bp.BPXODI2 IN (7, 9, 77, 99) THEN NULL ELSE bp.BPXODI2 END AS diastolic_bp_2,
    CASE WHEN bp.BPXOSY3 IN (7, 9, 77, 99) THEN NULL ELSE bp.BPXOSY3 END AS systolic_bp_3,
    CASE WHEN bp.BPXODI3 IN (7, 9, 77, 99) THEN NULL ELSE bp.BPXODI3 END AS diastolic_bp_3,
    
    -- ========== LAB - DIABETES (CLEAN SPECIAL CODES) ==========
    CASE WHEN ghb.LBXGH IN (7, 9, 77, 99) THEN NULL ELSE ghb.LBXGH END AS hba1c,
    CASE WHEN glu.LBXGLU IN (7, 9, 77, 99) THEN NULL ELSE glu.LBXGLU END AS fasting_glucose,
    CASE WHEN ins.LBXIN IN (7, 9, 77, 99) THEN NULL ELSE ins.LBXIN END AS fasting_insulin,
    
    -- ========== LAB - LIPIDS (CLEAN SPECIAL CODES) ==========
    CASE WHEN tchol.LBXTC IN (7, 9, 77, 99) THEN NULL ELSE tchol.LBXTC END AS total_cholesterol,
    CASE WHEN hdl.LBDHDD IN (7, 9, 77, 99) THEN NULL ELSE hdl.LBDHDD END AS hdl_cholesterol,
    CASE WHEN trig.LBXTLG IN (7, 9, 77, 99) THEN NULL ELSE trig.LBXTLG END AS triglycerides,
    CASE WHEN trig.LBDLDL IN (7, 9, 77, 99) THEN NULL ELSE trig.LBDLDL END AS ldl_cholesterol,
    
    -- ========== LAB - INFLAMMATION (CLEAN SPECIAL CODES) ==========
    CASE WHEN hscrp.LBXHSCRP IN (7, 9, 77, 99) THEN NULL ELSE hscrp.LBXHSCRP END AS c_reactive_protein,
    
    -- ========== DISEASE HISTORY (CLEAN SPECIAL CODES) ==========
    CASE WHEN diq.DIQ010 IN (7, 9, 77, 99) THEN NULL ELSE diq.DIQ010 END AS diabetes_told,
    CASE WHEN mcq.MCQ160E IN (7, 9, 77, 99) THEN NULL ELSE mcq.MCQ160E END AS coronary_heart_disease,
    CASE WHEN mcq.MCQ160F IN (7, 9, 77, 99) THEN NULL ELSE mcq.MCQ160F END AS heart_attack,
    CASE WHEN bpq.BPQ020 IN (7, 9, 77, 99) THEN NULL ELSE bpq.BPQ020 END AS hypertension_told,
    CASE WHEN bpq.BPQ080 IN (7, 9, 77, 99) THEN NULL ELSE bpq.BPQ080 END AS bp_medication,
    
    -- ========== SMOKING (CLEAN SPECIAL CODES) ==========
    CASE WHEN smq.SMQ020 IN (7, 9, 77, 99) THEN NULL ELSE smq.SMQ020 END AS ever_smoked_100,
    CASE WHEN smq.SMQ040 IN (7, 9, 77, 99, 777, 999) THEN NULL ELSE smq.SMQ040 END AS cigarettes_per_day,
    
    -- ========== PHYSICAL ACTIVITY (CLEAN SPECIAL CODES) ==========
    -- Note: 0 is valid for "no activity", but 7777/9999 are special codes
    CASE WHEN paq.PAD800 IN (7, 9, 77, 99, 777, 999, 7777, 9999) THEN NULL ELSE paq.PAD800 END AS moderate_activity_min,
    CASE WHEN paq.PAD820 IN (7, 9, 77, 99, 777, 999, 7777, 9999) THEN NULL ELSE paq.PAD820 END AS vigorous_activity_min,
    
    -- ========== ALCOHOL (CLEAN SPECIAL CODES) ==========
    CASE WHEN alq.ALQ111 IN (7, 9, 77, 99) THEN NULL ELSE alq.ALQ111 END AS drinks_past_year,
    CASE WHEN alq.ALQ130 IN (7, 9, 77, 99, 777, 999) THEN NULL ELSE alq.ALQ130 END AS avg_drinks_per_week,
    
    -- ========== DIET (CLEAN SPECIAL CODES) ==========
    CASE WHEN dbq.DBQ390 IN (7, 9, 77, 99, 777, 999) THEN NULL ELSE dbq.DBQ390 END AS fast_food_frequency,
    
    -- ========== DEPRESSION PHQ-9 (CLEAN SPECIAL CODES) ==========
    CASE WHEN dpq.DPQ010 IN (7, 9, 77, 99) THEN NULL ELSE dpq.DPQ010 END AS phq_little_interest,
    CASE WHEN dpq.DPQ020 IN (7, 9, 77, 99) THEN NULL ELSE dpq.DPQ020 END AS phq_feeling_down,
    CASE WHEN dpq.DPQ030 IN (7, 9, 77, 99) THEN NULL ELSE dpq.DPQ030 END AS phq_trouble_sleeping,
    CASE WHEN dpq.DPQ040 IN (7, 9, 77, 99) THEN NULL ELSE dpq.DPQ040 END AS phq_tired,
    CASE WHEN dpq.DPQ050 IN (7, 9, 77, 99) THEN NULL ELSE dpq.DPQ050 END AS phq_poor_appetite,
    CASE WHEN dpq.DPQ060 IN (7, 9, 77, 99) THEN NULL ELSE dpq.DPQ060 END AS phq_feeling_bad,
    CASE WHEN dpq.DPQ070 IN (7, 9, 77, 99) THEN NULL ELSE dpq.DPQ070 END AS phq_trouble_concentrating,
    CASE WHEN dpq.DPQ080 IN (7, 9, 77, 99) THEN NULL ELSE dpq.DPQ080 END AS phq_moving_slowly,
    CASE WHEN dpq.DPQ090 IN (7, 9, 77, 99) THEN NULL ELSE dpq.DPQ090 END AS phq_suicidal_thoughts,
    
    -- ========== SLEEP (CLEAN SPECIAL CODES) ==========
    -- NOTE: 7 and 9 appear in sleep data (refused/don't know), not just 77/99
    CASE WHEN slq.SLD012 IN (7, 9, 77, 99, 777, 999) THEN NULL ELSE slq.SLD012 END AS sleep_hours_weekday,
    CASE WHEN slq.SLD013 IN (7, 9, 77, 99, 777, 999) THEN NULL ELSE slq.SLD013 END AS sleep_hours_weekend

FROM demo d
LEFT JOIN bmx ON d.SEQN = bmx.SEQN
LEFT JOIN bpxo bp ON d.SEQN = bp.SEQN
LEFT JOIN ghb ON d.SEQN = ghb.SEQN
LEFT JOIN glu ON d.SEQN = glu.SEQN
LEFT JOIN ins ON d.SEQN = ins.SEQN
LEFT JOIN hdl ON d.SEQN = hdl.SEQN
LEFT JOIN trigly trig ON d.SEQN = trig.SEQN
LEFT JOIN tchol ON d.SEQN = tchol.SEQN
LEFT JOIN hscrp ON d.SEQN = hscrp.SEQN
LEFT JOIN diq ON d.SEQN = diq.SEQN
LEFT JOIN mcq ON d.SEQN = mcq.SEQN
LEFT JOIN bpq ON d.SEQN = bpq.SEQN
LEFT JOIN smq ON d.SEQN = smq.SEQN
LEFT JOIN paq ON d.SEQN = paq.SEQN
LEFT JOIN alq ON d.SEQN = alq.SEQN
LEFT JOIN dbq ON d.SEQN = dbq.SEQN
LEFT JOIN dpq ON d.SEQN = dpq.SEQN
LEFT JOIN slq ON d.SEQN = slq.SEQN;

SELECT 'Step 2A Complete' AS status, COUNT(*) AS total_rows FROM nhanes_master;

-- ============================================================================
-- STEP 2B: RANGE VALIDATION + DATA CLEANING
-- ============================================================================

CREATE TABLE nhanes_cleaned AS
SELECT 
    SEQN,
    
    -- ========== DEMOGRAPHICS ==========
    gender,
    age,
    race,
    education,
    marital_status,
    income_poverty_ratio,
    
    -- ========== BODY MEASUREMENTS (MEDICALLY PLAUSIBLE RANGES) ==========
    CASE WHEN weight_kg BETWEEN 30 AND 300 THEN weight_kg ELSE NULL END AS weight_kg,
    CASE WHEN height_cm BETWEEN 100 AND 220 THEN height_cm ELSE NULL END AS height_cm,
    CASE WHEN bmi BETWEEN 12 AND 75 THEN bmi ELSE NULL END AS bmi,
    CASE WHEN waist_cm BETWEEN 40 AND 200 THEN waist_cm ELSE NULL END AS waist_cm,
    
    -- ========== BLOOD PRESSURE (AVERAGED, MEDICALLY PLAUSIBLE) ==========
    CASE 
        WHEN systolic_bp_1 BETWEEN 70 AND 250 AND
             systolic_bp_2 BETWEEN 70 AND 250 AND
             systolic_bp_3 BETWEEN 70 AND 250
        THEN (systolic_bp_1 + systolic_bp_2 + systolic_bp_3) / 3
        WHEN systolic_bp_1 BETWEEN 70 AND 250 AND
             systolic_bp_2 BETWEEN 70 AND 250
        THEN (systolic_bp_1 + systolic_bp_2) / 2
        WHEN systolic_bp_1 BETWEEN 70 AND 250
        THEN systolic_bp_1
        ELSE NULL
    END AS systolic_bp,
    
    CASE 
        WHEN diastolic_bp_1 BETWEEN 30 AND 150 AND
             diastolic_bp_2 BETWEEN 30 AND 150 AND
             diastolic_bp_3 BETWEEN 30 AND 150
        THEN (diastolic_bp_1 + diastolic_bp_2 + diastolic_bp_3) / 3
        WHEN diastolic_bp_1 BETWEEN 30 AND 150 AND
             diastolic_bp_2 BETWEEN 30 AND 150
        THEN (diastolic_bp_1 + diastolic_bp_2) / 2
        WHEN diastolic_bp_1 BETWEEN 30 AND 150
        THEN diastolic_bp_1
        ELSE NULL
    END AS diastolic_bp,
    
    -- ========== LAB VALUES (MEDICALLY PLAUSIBLE RANGES) ==========
    CASE WHEN hba1c BETWEEN 3 AND 20 THEN hba1c ELSE NULL END AS hba1c,
    CASE WHEN fasting_glucose BETWEEN 40 AND 600 THEN fasting_glucose ELSE NULL END AS fasting_glucose,
    CASE WHEN fasting_insulin BETWEEN 1 AND 300 THEN fasting_insulin ELSE NULL END AS fasting_insulin,
    CASE WHEN total_cholesterol BETWEEN 80 AND 600 THEN total_cholesterol ELSE NULL END AS total_cholesterol,
    CASE WHEN hdl_cholesterol BETWEEN 10 AND 150 THEN hdl_cholesterol ELSE NULL END AS hdl_cholesterol,
    CASE WHEN triglycerides BETWEEN 20 AND 1000 THEN triglycerides ELSE NULL END AS triglycerides,
    CASE WHEN ldl_cholesterol BETWEEN 20 AND 500 THEN ldl_cholesterol ELSE NULL END AS ldl_cholesterol,
    CASE WHEN c_reactive_protein BETWEEN 0.1 AND 50 THEN c_reactive_protein ELSE NULL END AS c_reactive_protein,
    
    -- ========== DISEASE LABELS (BINARY 0/1) ==========
    CASE 
        WHEN diabetes_told = 1 THEN 1
        WHEN diabetes_told = 2 THEN 0
        WHEN diabetes_told = 3 THEN 0  -- Borderline = prediabetes
        ELSE NULL
    END AS diabetes_diagnosed,
    
    CASE 
        WHEN coronary_heart_disease = 1 OR heart_attack = 1 THEN 1
        WHEN coronary_heart_disease = 2 AND heart_attack = 2 THEN 0
        ELSE NULL
    END AS cvd_history,
    
    CASE 
        WHEN hypertension_told = 1 THEN 1
        WHEN hypertension_told = 2 THEN 0
        ELSE NULL
    END AS hypertension_diagnosed,
    
    CASE 
        WHEN bp_medication = 1 THEN 1
        WHEN bp_medication = 2 THEN 0
        ELSE 0
    END AS on_bp_medication,
    
    -- ========== SMOKING STATUS ==========
    CASE 
        WHEN ever_smoked_100 = 1 AND cigarettes_per_day > 0 THEN 1  -- Current
        WHEN ever_smoked_100 = 1 AND (cigarettes_per_day = 0 OR cigarettes_per_day IS NULL) THEN 2  -- Former
        WHEN ever_smoked_100 = 2 THEN 0  -- Never
        ELSE NULL
    END AS smoking_status,
    
    CASE WHEN cigarettes_per_day BETWEEN 0 AND 100 THEN cigarettes_per_day ELSE NULL END AS cigarettes_per_day,
    
    -- ========== PHYSICAL ACTIVITY (0 is valid = no activity) ==========
    CASE WHEN moderate_activity_min BETWEEN 0 AND 3000 THEN moderate_activity_min ELSE NULL END AS moderate_activity_min,
    CASE WHEN vigorous_activity_min BETWEEN 0 AND 3000 THEN vigorous_activity_min ELSE NULL END AS vigorous_activity_min,
    
    -- ========== ALCOHOL (0 is valid = no drinking) ==========
    CASE 
        WHEN drinks_past_year = 1 AND avg_drinks_per_week > 0 THEN avg_drinks_per_week
        WHEN drinks_past_year = 2 THEN 0  -- Explicitly said no drinks
        WHEN avg_drinks_per_week BETWEEN 0 AND 50 THEN avg_drinks_per_week
        ELSE NULL
    END AS alcohol_drinks_per_week,
    
    -- ========== DIET ==========
    CASE WHEN fast_food_frequency BETWEEN 0 AND 21 THEN fast_food_frequency ELSE NULL END AS fast_food_times_per_week,
    
    -- ========== PHQ-9 DEPRESSION SCORE (0-27) ==========
    CASE 
        WHEN phq_little_interest BETWEEN 0 AND 3 AND
             phq_feeling_down BETWEEN 0 AND 3 AND
             phq_trouble_sleeping BETWEEN 0 AND 3 AND
             phq_tired BETWEEN 0 AND 3 AND
             phq_poor_appetite BETWEEN 0 AND 3 AND
             phq_feeling_bad BETWEEN 0 AND 3 AND
             phq_trouble_concentrating BETWEEN 0 AND 3 AND
             phq_moving_slowly BETWEEN 0 AND 3 AND
             phq_suicidal_thoughts BETWEEN 0 AND 3
        THEN 
            COALESCE(phq_little_interest, 0) +
            COALESCE(phq_feeling_down, 0) +
            COALESCE(phq_trouble_sleeping, 0) +
            COALESCE(phq_tired, 0) +
            COALESCE(phq_poor_appetite, 0) +
            COALESCE(phq_feeling_bad, 0) +
            COALESCE(phq_trouble_concentrating, 0) +
            COALESCE(phq_moving_slowly, 0) +
            COALESCE(phq_suicidal_thoughts, 0)
        ELSE NULL
    END AS depression_score,
    
    -- ========== SLEEP (2-16 hours is medically plausible) ==========
    CASE WHEN sleep_hours_weekday BETWEEN 2 AND 16 THEN sleep_hours_weekday ELSE NULL END AS sleep_hours_weekday,
    CASE WHEN sleep_hours_weekend BETWEEN 2 AND 16 THEN sleep_hours_weekend ELSE NULL END AS sleep_hours_weekend

FROM nhanes_master

WHERE 
    -- QUALITY FILTERS
    exam_status = 2                     -- Examined (not interview-only)
    AND age >= 18                       -- Adults only
    AND (pregnancy_status != 1 OR pregnancy_status IS NULL)  -- Exclude pregnant
    AND bmi IS NOT NULL                 -- Must have BMI
    AND SEQN > 0                        -- Valid SEQN
    AND (hba1c IS NOT NULL OR fasting_glucose IS NOT NULL OR systolic_bp_1 IS NOT NULL);

SELECT 'Step 2B Complete' AS status, COUNT(*) AS total_rows FROM nhanes_cleaned;

-- ============================================================================
-- STEP 2C: REMOVE DUPLICATES
-- ============================================================================

CREATE TABLE nhanes_final AS
SELECT * FROM nhanes_cleaned
GROUP BY SEQN;

DROP TABLE nhanes_cleaned;
ALTER TABLE nhanes_final RENAME TO nhanes_cleaned;

SELECT 'Step 2C Complete' AS status, COUNT(*) AS total_rows FROM nhanes_cleaned;

-- ============================================================================
-- STEP 2D: CREATE TARGET VARIABLES
-- ============================================================================

ALTER TABLE nhanes_cleaned
ADD COLUMN diabetes_stage INT,
ADD COLUMN hypertension_stage INT,
ADD COLUMN metabolic_syndrome INT,
ADD COLUMN depression_category VARCHAR(20),
ADD COLUMN total_activity_min INT;

UPDATE nhanes_cleaned SET
    diabetes_stage = CASE
        WHEN diabetes_diagnosed = 1 THEN 2
        WHEN hba1c >= 6.5 THEN 2
        WHEN fasting_glucose >= 126 THEN 2
        WHEN hba1c BETWEEN 5.7 AND 6.4 THEN 1
        WHEN fasting_glucose BETWEEN 100 AND 125 THEN 1
        ELSE 0
    END,
    
    hypertension_stage = CASE
        WHEN systolic_bp >= 140 OR diastolic_bp >= 90 THEN 3
        WHEN systolic_bp >= 130 OR diastolic_bp >= 80 THEN 2
        WHEN systolic_bp >= 120 THEN 1
        ELSE 0
    END,
    
    metabolic_syndrome = CASE
        WHEN (
            (CASE WHEN waist_cm > 102 AND gender = 1 THEN 1 WHEN waist_cm > 88 AND gender = 2 THEN 1 ELSE 0 END) +
            (CASE WHEN triglycerides >= 150 THEN 1 ELSE 0 END) +
            (CASE WHEN hdl_cholesterol < 40 AND gender = 1 THEN 1 WHEN hdl_cholesterol < 50 AND gender = 2 THEN 1 ELSE 0 END) +
            (CASE WHEN systolic_bp >= 130 OR diastolic_bp >= 85 OR on_bp_medication = 1 THEN 1 ELSE 0 END) +
            (CASE WHEN fasting_glucose >= 100 THEN 1 ELSE 0 END)
        ) >= 3 THEN 1 ELSE 0
    END,
    
    depression_category = CASE
        WHEN depression_score >= 20 THEN 'Severe'
        WHEN depression_score >= 15 THEN 'Moderately Severe'
        WHEN depression_score >= 10 THEN 'Moderate'
        WHEN depression_score >= 5 THEN 'Mild'
        ELSE 'None'
    END,
    
    total_activity_min = COALESCE(moderate_activity_min, 0) + COALESCE(vigorous_activity_min, 0);

SELECT 'Step 2D Complete' AS status;

-- ============================================================================
-- FINAL VERIFICATION
-- ============================================================================

SELECT '========== FINAL DATASET SUMMARY ==========' AS '';

SELECT 
    COUNT(*) AS total_records,
    COUNT(DISTINCT SEQN) AS unique_seqn,
    ROUND(AVG(age), 1) AS avg_age,
    SUM(CASE WHEN gender = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100 AS male_pct
FROM nhanes_cleaned;

SELECT 
    SUM(diabetes_stage = 0) AS normal_glucose,
    SUM(diabetes_stage = 1) AS prediabetes,
    SUM(diabetes_stage = 2) AS diabetes,
    SUM(cvd_history = 1) AS cvd_cases,
    SUM(hypertension_stage >= 2) AS hypertension_cases,
    SUM(metabolic_syndrome = 1) AS metabolic_syndrome_cases
FROM nhanes_cleaned;

SELECT * FROM nhanes_cleaned LIMIT 5;

SELECT '========== READY FOR STEP 3 (PYTHON FEATURE ENGINEERING) ==========' AS '';

-- ============================================================================
-- DONE! Table nhanes_cleaned is now COMPLETELY CLEAN
-- ============================================================================
