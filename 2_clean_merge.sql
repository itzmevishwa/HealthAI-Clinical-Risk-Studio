-- ============================================================================
-- NHANES PROJECT - STEP 2 (CORRECTLY FIXED)
-- Special codes removed ONLY where verified as refused/don't know
-- Lab and examination values use RANGE VALIDATION ONLY
-- Based on deep analysis of actual value distributions in each XPT file
-- ============================================================================
-- KEY PRINCIPLE:
--   Questionnaire columns → remove 7/9/77/99 (verified refused/don't know)
--   Lab/examination columns → range validation ONLY (7,9,77,99 are real values)
-- ============================================================================

SET sql_mode = '';
SET SESSION group_concat_max_len = 1000000;

USE nhanes_project;

DROP TABLE IF EXISTS nhanes_master;
DROP TABLE IF EXISTS nhanes_cleaned;
DROP TABLE IF EXISTS nhanes_final;

-- ============================================================================
-- STEP 2A: MERGE ALL TABLES
-- ============================================================================

CREATE TABLE nhanes_master AS
SELECT
    d.SEQN,

    -- ========== DEMOGRAPHICS ==========
    -- RIAGENDR: 1=Male, 2=Female only. No 7/9 found in data → keep as-is
    d.RIDSTATR  AS exam_status,
    d.RIAGENDR  AS gender,
    d.RIDAGEYR  AS age,
    d.RIDRETH3  AS race,
    -- DMDEDUC2: 7=Refused, 9=Don't know → remove (verified questionnaire codes)
    CASE WHEN d.DMDEDUC2 IN (7,9) THEN NULL ELSE d.DMDEDUC2 END AS education,
    -- DMDMARTZ: 77=Refused, 99=Don't know → remove
    CASE WHEN d.DMDMARTZ IN (77,99) THEN NULL ELSE d.DMDMARTZ END AS marital_status,
    d.INDFMPIR  AS income_poverty_ratio,
    d.RIDEXPRG  AS pregnancy_status,

    -- ========== BODY MEASUREMENTS ==========
    -- BMXWT, BMXHT, BMXWAIST: 7,9,77,99 are REAL weights/heights/waists
    -- Example: weight=77kg, height=99cm are valid → DO NOT remove
    -- Use range validation only
    bmx.BMXWT    AS weight_kg,
    bmx.BMXHT    AS height_cm,
    bmx.BMXBMI   AS bmi,
    bmx.BMXWAIST AS waist_cm,

    -- ========== BLOOD PRESSURE ==========
    -- BPXOSY1/BPXODI1: 77, 99 are real BP values (77/99 mmHg)
    -- Use range validation only - NO special code removal
    bp.BPXOSY1 AS systolic_bp_1,
    bp.BPXODI1 AS diastolic_bp_1,
    bp.BPXOSY2 AS systolic_bp_2,
    bp.BPXODI2 AS diastolic_bp_2,
    bp.BPXOSY3 AS systolic_bp_3,
    bp.BPXODI3 AS diastolic_bp_3,

    -- ========== LAB VALUES ==========
    -- ALL lab values: 7,9,77,99 are REAL medical values
    -- e.g. HbA1c=7.0% = diabetic, Glucose=99 = prediabetes, HDL=77 = real
    -- Use range validation only - NO special code removal
    ghb.LBXGH       AS hba1c,
    glu.LBXGLU      AS fasting_glucose,
    ins.LBXIN       AS fasting_insulin,
    tchol.LBXTC     AS total_cholesterol,
    hdl.LBDHDD      AS hdl_cholesterol,
    trig.LBXTLG     AS triglycerides,
    trig.LBDLDL     AS ldl_cholesterol,
    hscrp.LBXHSCRP  AS c_reactive_protein,

    -- ========== QUESTIONNAIRE - DISEASE HISTORY ==========
    -- DIQ010: 1=Yes, 2=No, 3=Borderline, 9=Don't know (4 rows) → remove 9
    CASE WHEN diq.DIQ010 = 9 THEN NULL ELSE diq.DIQ010 END AS diabetes_told,

    -- MCQ160E/F: 1=Yes, 2=No, 9=Don't know → remove 9
    CASE WHEN mcq.MCQ160E = 9 THEN NULL ELSE mcq.MCQ160E END AS coronary_heart_disease,
    CASE WHEN mcq.MCQ160F = 9 THEN NULL ELSE mcq.MCQ160F END AS heart_attack,

    -- BPQ020: 1=Yes, 2=No, 7=Refused(1 row), 9=Don't know(10 rows) → remove 7,9
    CASE WHEN bpq.BPQ020 IN (7,9) THEN NULL ELSE bpq.BPQ020 END AS hypertension_told,
    -- BPQ080: 1=Yes, 2=No, 7=Refused(1), 9=Don't know(53) → remove 7,9
    CASE WHEN bpq.BPQ080 IN (7,9) THEN NULL ELSE bpq.BPQ080 END AS bp_medication,

    -- ========== QUESTIONNAIRE - SMOKING ==========
    -- SMQ020: 1=Yes, 2=No, 7=Refused(7), 9=Don't know(7) → remove 7,9
    CASE WHEN smq.SMQ020 IN (7,9) THEN NULL ELSE smq.SMQ020 END AS ever_smoked_100,
    -- SMQ040: 1=Every day, 2=Some days, 3=Not at all → NO 7/9 found, keep as-is
    smq.SMQ040 AS smoking_now,

    -- ========== QUESTIONNAIRE - PHYSICAL ACTIVITY ==========
    -- PAD800: values are real minutes (1,2,3...600 min/week) + 9999=Don't know
    -- 7 appears as real value (7 minutes) - DO NOT remove 7
    -- Only remove 9999 (Don't know confirmed in NHANES codebook)
    CASE WHEN paq.PAD800 = 9999 THEN NULL ELSE paq.PAD800 END AS moderate_activity_min,
    -- PAD820: same - 7777=Refused(1 row), 9999=Don't know(13 rows)
    CASE WHEN paq.PAD820 IN (7777,9999) THEN NULL ELSE paq.PAD820 END AS vigorous_activity_min,

    -- ========== QUESTIONNAIRE - ALCOHOL ==========
    -- ALQ111: 1=Yes, 2=No, 9=Don't know(5 rows) → remove 9
    CASE WHEN alq.ALQ111 = 9 THEN NULL ELSE alq.ALQ111 END AS drinks_past_year,
    -- ALQ130: 1-15 are real drink counts + 777=Refused(4), 999=Don't know(10) → remove 777,999
    -- NOTE: 7 drinks/week and 9 drinks/week are REAL values - DO NOT remove!
    CASE WHEN alq.ALQ130 IN (777,999) THEN NULL ELSE alq.ALQ130 END AS avg_drinks_per_week,

    -- ========== QUESTIONNAIRE - DIET ==========
    -- DBQ390: 1=Never, 2=<1/week, 3=1-3/week, 9=Don't know(9 rows) → remove 9
    CASE WHEN dbq.DBQ390 = 9 THEN NULL ELSE dbq.DBQ390 END AS fast_food_frequency,

    -- ========== QUESTIONNAIRE - DEPRESSION PHQ-9 ==========
    -- DPQ010-DPQ090: 0,1,2,3 are valid scores. 7=Refused, 9=Don't know → remove 7,9
    -- NOTE: the 5.39e-79 value is NHANES encoding for 0 (zero) - keep it, treat as 0
    CASE WHEN dpq.DPQ010 IN (7,9) THEN NULL ELSE dpq.DPQ010 END AS phq_little_interest,
    CASE WHEN dpq.DPQ020 IN (7,9) THEN NULL ELSE dpq.DPQ020 END AS phq_feeling_down,
    CASE WHEN dpq.DPQ030 IN (7,9) THEN NULL ELSE dpq.DPQ030 END AS phq_trouble_sleeping,
    CASE WHEN dpq.DPQ040 IN (7,9) THEN NULL ELSE dpq.DPQ040 END AS phq_tired,
    CASE WHEN dpq.DPQ050 IN (7,9) THEN NULL ELSE dpq.DPQ050 END AS phq_poor_appetite,
    CASE WHEN dpq.DPQ060 IN (7,9) THEN NULL ELSE dpq.DPQ060 END AS phq_feeling_bad,
    CASE WHEN dpq.DPQ070 IN (7,9) THEN NULL ELSE dpq.DPQ070 END AS phq_trouble_concentrating,
    CASE WHEN dpq.DPQ080 IN (7,9) THEN NULL ELSE dpq.DPQ080 END AS phq_moving_slowly,
    CASE WHEN dpq.DPQ090 IN (7,9) THEN NULL ELSE dpq.DPQ090 END AS phq_suicidal_thoughts,

    -- ========== QUESTIONNAIRE - SLEEP ==========
    -- SLD012/SLD013: values range 2.0 to 14.0 hours only
    -- NO 7, 9, 77, 99 found in actual data → keep as-is, use range validation
    slq.SLD012 AS sleep_hours_weekday,
    slq.SLD013 AS sleep_hours_weekend

FROM demo d
LEFT JOIN bmx   ON d.SEQN = bmx.SEQN
LEFT JOIN bpxo bp ON d.SEQN = bp.SEQN
LEFT JOIN ghb   ON d.SEQN = ghb.SEQN
LEFT JOIN glu   ON d.SEQN = glu.SEQN
LEFT JOIN ins   ON d.SEQN = ins.SEQN
LEFT JOIN hdl   ON d.SEQN = hdl.SEQN
LEFT JOIN trigly trig ON d.SEQN = trig.SEQN
LEFT JOIN tchol ON d.SEQN = tchol.SEQN
LEFT JOIN hscrp ON d.SEQN = hscrp.SEQN
LEFT JOIN diq   ON d.SEQN = diq.SEQN
LEFT JOIN mcq   ON d.SEQN = mcq.SEQN
LEFT JOIN bpq   ON d.SEQN = bpq.SEQN
LEFT JOIN smq   ON d.SEQN = smq.SEQN
LEFT JOIN paq   ON d.SEQN = paq.SEQN
LEFT JOIN alq   ON d.SEQN = alq.SEQN
LEFT JOIN dbq   ON d.SEQN = dbq.SEQN
LEFT JOIN dpq   ON d.SEQN = dpq.SEQN
LEFT JOIN slq   ON d.SEQN = slq.SEQN;

SELECT 'Step 2A Complete' AS status, COUNT(*) AS total_rows FROM nhanes_master;

-- ============================================================================
-- STEP 2B: RANGE VALIDATION + CLEAN TABLE
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

    -- ========== BODY MEASUREMENTS (range validation only) ==========
    CASE WHEN weight_kg BETWEEN 30 AND 300 THEN weight_kg ELSE NULL END AS weight_kg,
    CASE WHEN height_cm BETWEEN 100 AND 220 THEN height_cm ELSE NULL END AS height_cm,
    CASE WHEN bmi BETWEEN 12 AND 75 THEN bmi ELSE NULL END AS bmi,
    CASE WHEN waist_cm BETWEEN 40 AND 200 THEN waist_cm ELSE NULL END AS waist_cm,

    -- ========== BLOOD PRESSURE (range validation + averaging) ==========
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

    -- ========== LAB VALUES (range validation only - no special code removal) ==========
    CASE WHEN hba1c BETWEEN 3 AND 20 THEN hba1c ELSE NULL END AS hba1c,
    CASE WHEN fasting_glucose BETWEEN 40 AND 600 THEN fasting_glucose ELSE NULL END AS fasting_glucose,
    CASE WHEN fasting_insulin BETWEEN 1 AND 300 THEN fasting_insulin ELSE NULL END AS fasting_insulin,
    CASE WHEN total_cholesterol BETWEEN 80 AND 600 THEN total_cholesterol ELSE NULL END AS total_cholesterol,
    CASE WHEN hdl_cholesterol BETWEEN 10 AND 150 THEN hdl_cholesterol ELSE NULL END AS hdl_cholesterol,
    CASE WHEN triglycerides BETWEEN 20 AND 1000 THEN triglycerides ELSE NULL END AS triglycerides,
    CASE WHEN ldl_cholesterol BETWEEN 20 AND 500 THEN ldl_cholesterol ELSE NULL END AS ldl_cholesterol,
    CASE WHEN c_reactive_protein BETWEEN 0.1 AND 50 THEN c_reactive_protein ELSE NULL END AS c_reactive_protein,

    -- ========== DISEASE LABELS (binary 0/1) ==========
    CASE
        WHEN diabetes_told = 1 THEN 1
        WHEN diabetes_told = 2 THEN 0
        WHEN diabetes_told = 3 THEN 0  -- borderline = not yet diabetic
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
    -- SMQ020: 1=ever smoked, 2=never. SMQ040: 1=every day, 2=some days, 3=not at all
    CASE
        WHEN ever_smoked_100 = 1 AND smoking_now IN (1,2) THEN 1  -- current smoker
        WHEN ever_smoked_100 = 1 AND smoking_now = 3      THEN 2  -- former smoker
        WHEN ever_smoked_100 = 2                          THEN 0  -- never smoked
        ELSE NULL
    END AS smoking_status,

    -- ========== PHYSICAL ACTIVITY (0 is valid = no activity) ==========
    CASE WHEN moderate_activity_min BETWEEN 0 AND 3000 THEN moderate_activity_min ELSE NULL END AS moderate_activity_min,
    CASE WHEN vigorous_activity_min BETWEEN 0 AND 3000 THEN vigorous_activity_min ELSE NULL END AS vigorous_activity_min,

    -- ========== ALCOHOL ==========
    -- 7,9 drinks/week are REAL values kept. Only 777,999 removed in Step 2A.
    CASE
        WHEN drinks_past_year = 2 THEN 0       -- explicitly said no drinks
        WHEN avg_drinks_per_week BETWEEN 0 AND 50 THEN avg_drinks_per_week
        ELSE NULL
    END AS alcohol_drinks_per_week,

    -- ========== DIET ==========
    -- 1=never, 2=less than once/week, 3=1-3/week. 9 removed in Step 2A.
    CASE WHEN fast_food_frequency BETWEEN 1 AND 3 THEN fast_food_frequency ELSE NULL END AS fast_food_frequency,

    -- ========== PHQ-9 DEPRESSION SCORE ==========
    -- Valid scores: 0-3 per item. 7,9 removed in Step 2A.
    -- The tiny value ~5.4e-79 in data is NHANES encoding for 0 → treated as 0 by BETWEEN
    CASE
        WHEN phq_little_interest    BETWEEN 0 AND 3 AND
             phq_feeling_down       BETWEEN 0 AND 3 AND
             phq_trouble_sleeping   BETWEEN 0 AND 3 AND
             phq_tired              BETWEEN 0 AND 3 AND
             phq_poor_appetite      BETWEEN 0 AND 3 AND
             phq_feeling_bad        BETWEEN 0 AND 3 AND
             phq_trouble_concentrating BETWEEN 0 AND 3 AND
             phq_moving_slowly      BETWEEN 0 AND 3 AND
             phq_suicidal_thoughts  BETWEEN 0 AND 3
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

    -- ========== SLEEP (range validation only - no special codes in data) ==========
    CASE WHEN sleep_hours_weekday BETWEEN 2 AND 16 THEN sleep_hours_weekday ELSE NULL END AS sleep_hours_weekday,
    CASE WHEN sleep_hours_weekend BETWEEN 2 AND 16 THEN sleep_hours_weekend ELSE NULL END AS sleep_hours_weekend

FROM nhanes_master

WHERE
    exam_status = 2
    AND age >= 18
    AND (pregnancy_status != 1 OR pregnancy_status IS NULL)
    AND bmi IS NOT NULL
    AND SEQN > 0
    AND (hba1c IS NOT NULL OR fasting_glucose IS NOT NULL OR systolic_bp_1 IS NOT NULL);

SELECT 'Step 2B Complete' AS status, COUNT(*) AS total_rows FROM nhanes_cleaned;

-- ============================================================================
-- STEP 2C: REMOVE DUPLICATES
-- ============================================================================

CREATE TABLE nhanes_final AS
SELECT * FROM nhanes_cleaned GROUP BY SEQN;

DROP TABLE nhanes_cleaned;
ALTER TABLE nhanes_final RENAME TO nhanes_cleaned;

SELECT 'Step 2C Complete' AS status, COUNT(*) AS total_rows FROM nhanes_cleaned;

-- ============================================================================
-- STEP 2D: CREATE TARGET VARIABLES
-- ============================================================================

ALTER TABLE nhanes_cleaned
ADD COLUMN diabetes_stage      INT,
ADD COLUMN hypertension_stage  INT,
ADD COLUMN metabolic_syndrome  INT,
ADD COLUMN obesity_stage       INT,
ADD COLUMN depression_category VARCHAR(20),
ADD COLUMN total_activity_min  INT;

UPDATE nhanes_cleaned SET

    diabetes_stage = CASE
        WHEN diabetes_diagnosed = 1  THEN 2
        WHEN hba1c >= 6.5            THEN 2
        WHEN fasting_glucose >= 126  THEN 2
        WHEN hba1c BETWEEN 5.7 AND 6.4       THEN 1
        WHEN fasting_glucose BETWEEN 100 AND 125 THEN 1
        ELSE 0
    END,

    hypertension_stage = CASE
        WHEN systolic_bp >= 140 OR diastolic_bp >= 90 THEN 3
        WHEN systolic_bp >= 130 OR diastolic_bp >= 80 THEN 2
        WHEN systolic_bp >= 120                        THEN 1
        ELSE 0
    END,

    metabolic_syndrome = CASE
        WHEN (
            (CASE WHEN waist_cm > 102 AND gender = 1 THEN 1
                  WHEN waist_cm > 88  AND gender = 2 THEN 1
                  ELSE 0 END) +
            (CASE WHEN triglycerides >= 150 THEN 1 ELSE 0 END) +
            (CASE WHEN hdl_cholesterol < 40 AND gender = 1 THEN 1
                  WHEN hdl_cholesterol < 50 AND gender = 2 THEN 1
                  ELSE 0 END) +
            (CASE WHEN systolic_bp >= 130 OR diastolic_bp >= 85
                       OR on_bp_medication = 1 THEN 1 ELSE 0 END) +
            (CASE WHEN fasting_glucose >= 100 THEN 1 ELSE 0 END)
        ) >= 3 THEN 1 ELSE 0
    END,

    depression_category = CASE
        WHEN depression_score >= 20 THEN 'Severe'
        WHEN depression_score >= 15 THEN 'Moderately Severe'
        WHEN depression_score >= 10 THEN 'Moderate'
        WHEN depression_score >= 5  THEN 'Mild'
        ELSE 'None'
    END,

    obesity_stage = CASE
        WHEN bmi < 18.5 THEN 0   -- Underweight
        WHEN bmi < 25   THEN 1   -- Normal
        WHEN bmi < 30   THEN 2   -- Overweight
        WHEN bmi >= 30  THEN 3   -- Obese
        ELSE NULL
    END,

    total_activity_min = COALESCE(moderate_activity_min, 0)
                       + COALESCE(vigorous_activity_min, 0);

SELECT 'Step 2D Complete' AS status;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT '====== FINAL DATASET SUMMARY ======' AS '';

SELECT
    COUNT(*)                    AS total_records,
    COUNT(DISTINCT SEQN)        AS unique_patients,
    ROUND(AVG(age), 1)          AS avg_age,
    ROUND(AVG(bmi), 1)          AS avg_bmi,
    ROUND(SUM(CASE WHEN gender=1 THEN 1 ELSE 0 END)/COUNT(*)*100,1) AS male_pct
FROM nhanes_cleaned;

SELECT
    SUM(diabetes_stage = 0)        AS normal_glucose,
    SUM(diabetes_stage = 1)        AS prediabetes,
    SUM(diabetes_stage = 2)        AS diabetes,
    SUM(cvd_history = 1)           AS cvd_cases,
    SUM(hypertension_stage >= 2)   AS hypertension_cases,
    SUM(metabolic_syndrome = 1)    AS metabolic_syndrome_cases,
    SUM(obesity_stage = 3)         AS obese_cases
FROM nhanes_cleaned;

SELECT * FROM nhanes_cleaned LIMIT 5;

SELECT '====== READY FOR STEP 3 ======' AS '';

-- ============================================================================
-- SUMMARY OF WHAT WAS DONE CORRECTLY
-- ============================================================================
-- Lab values (HbA1c, glucose, cholesterol, BP, BMI):
--   → Range validation ONLY. No special code removal.
--   → Reason: 7,9,77,99 are valid medical values in these columns.
--
-- Questionnaire columns: special codes removed where verified:
--   → DIQ010: 9 removed (4 rows)
--   → MCQ160E/F: 9 removed
--   → BPQ020/080: 7,9 removed
--   → SMQ020: 7,9 removed
--   → ALQ111: 9 removed
--   → ALQ130: 777,999 removed (7,9 drinks/week are real values)
--   → PAD800: 9999 removed (7 minutes is a real value)
--   → PAD820: 7777,9999 removed
--   → DBQ390: 9 removed
--   → DPQ010-090: 7,9 removed
--   → Sleep (SLD012/013): NO special codes found → kept as-is
-- ============================================================================