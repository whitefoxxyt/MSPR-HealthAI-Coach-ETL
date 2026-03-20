import pandas as pd

from cleaners.diet_recommendations import clean


def _make_df(overrides=None):
    base = {
        "Patient_ID": "P001",
        "Age": "45",
        "Gender": "Male",
        "Weight_kg": "80",
        "Height_cm": "175",
        "BMI": "26.1",
        "Disease_Type": "Diabetes",
        "Severity": "Moderate",
        "Physical_Activity_Level": "Medium",
        "Daily_Caloric_Intake": "2000",
        "Cholesterol_mg/dL": "200",
        "Blood_Pressure_mmHg": "120",
        "Glucose_mg/dL": "110",
        "Dietary_Restrictions": "None",
        "Allergies": "None",
        "Preferred_Cuisine": "Mediterranean",
        "Weekly_Exercise_Hours": "5",
        "Adherence_to_Diet_Plan": "0.8",
        "Dietary_Nutrient_Imbalance_Score": "0.3",
        "Diet_Recommendation": "Low sugar",
    }
    if overrides:
        base.update(overrides)
    return pd.DataFrame([base])


class TestDietRecommendationsCleaner:
    def test_valid_row_accepted(self):
        clean_df, rejected_df = clean(_make_df())
        assert len(clean_df) == 1
        assert len(rejected_df) == 0

    def test_missing_patient_id_rejected(self):
        clean_df, rejected_df = clean(_make_df({"Patient_ID": ""}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
        assert "Patient_ID" in rejected_df.iloc[0]["reason"]

    def test_weight_out_of_bounds_rejected(self):
        clean_df, rejected_df = clean(_make_df({"Weight_kg": "500"}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
        assert "weight_kg" in rejected_df.iloc[0]["reason"]

    def test_height_out_of_bounds_rejected(self):
        clean_df, rejected_df = clean(_make_df({"Height_cm": "300"}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
        assert "height_cm" in rejected_df.iloc[0]["reason"]

    def test_bmi_out_of_bounds_rejected(self):
        clean_df, rejected_df = clean(_make_df({"BMI": "100"}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
        assert "bmi" in rejected_df.iloc[0]["reason"]

    def test_patient_id_mapped(self):
        clean_df, _ = clean(_make_df())
        assert clean_df.iloc[0]["external_patient_id"] == "P001"

    def test_multiple_violations_reported(self):
        clean_df, rejected_df = clean(_make_df({"Weight_kg": "500", "Height_cm": "300"}))
        assert len(rejected_df) == 1
        reason = rejected_df.iloc[0]["reason"]
        assert "weight_kg" in reason
        assert "height_cm" in reason

    def test_none_values_pass(self):
        clean_df, _ = clean(_make_df({"Weight_kg": "", "Height_cm": "", "BMI": ""}))
        assert len(clean_df) == 1
        assert pd.isna(clean_df.iloc[0]["weight_kg"])
        assert pd.isna(clean_df.iloc[0]["height_cm"])
        assert pd.isna(clean_df.iloc[0]["bmi"])
