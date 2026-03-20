import pandas as pd

from cleaners.gym_tracking import clean


def _make_df(overrides=None):
    base = {
        "Workout_Type": "Cardio",
        "Session_Duration (hours)": "1.5",
        "Calories_Burned": "500",
        "Weight (kg)": "75",
        "Height (m)": "1.80",
        "BMI": "23.1",
        "Fat_Percentage": "18.5",
        "Avg_BPM": "140",
        "Max_BPM": "175",
        "Resting_BPM": "65",
    }
    if overrides:
        base.update(overrides)
    return pd.DataFrame([base])


class TestGymTrackingCleaner:
    def test_valid_row_accepted(self):
        clean_df, rejected_df = clean(_make_df())
        assert len(clean_df) == 1
        assert len(rejected_df) == 0

    def test_status_nettoye(self):
        clean_df, _ = clean(_make_df())
        assert clean_df.iloc[0]["status"] == "NETTOYE"

    def test_hours_to_minutes_conversion(self):
        clean_df, _ = clean(_make_df({"Session_Duration (hours)": "1.5"}))
        assert clean_df.iloc[0]["duration_min"] == 90.0

    def test_meters_to_centimeters_conversion(self):
        clean_df, _ = clean(_make_df({"Height (m)": "1.80"}))
        assert clean_df.iloc[0]["height_cm"] == 180.0

    def test_missing_workout_type_rejected(self):
        clean_df, rejected_df = clean(_make_df({"Workout_Type": ""}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1

    def test_weight_out_of_bounds_rejected(self):
        clean_df, rejected_df = clean(_make_df({"Weight (kg)": "500"}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
        assert "weight_kg" in rejected_df.iloc[0]["reason"]

    def test_heart_rate_out_of_bounds_rejected(self):
        clean_df, rejected_df = clean(_make_df({"Avg_BPM": "300"}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
        assert "heart_rate" in rejected_df.iloc[0]["reason"]

    def test_bmi_out_of_bounds_rejected(self):
        clean_df, rejected_df = clean(_make_df({"BMI": "100"}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
        assert "bmi" in rejected_df.iloc[0]["reason"]

    def test_fat_percentage_out_of_bounds_rejected(self):
        clean_df, rejected_df = clean(_make_df({"Fat_Percentage": "80"}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
        assert "fat_percentage" in rejected_df.iloc[0]["reason"]

    def test_duration_out_of_bounds_rejected(self):
        clean_df, rejected_df = clean(_make_df({"Session_Duration (hours)": "10"}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
        assert "duration_min" in rejected_df.iloc[0]["reason"]

    def test_height_out_of_bounds_rejected(self):
        clean_df, rejected_df = clean(_make_df({"Height (m)": "3.0"}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
        assert "height_cm" in rejected_df.iloc[0]["reason"]

    def test_exercise_fields_present(self):
        clean_df, _ = clean(_make_df())
        assert "workout_type" in clean_df.columns
        assert "duration_min" in clean_df.columns
        assert "calories_burned" in clean_df.columns
        assert "heart_rate_avg" in clean_df.columns
        assert "heart_rate_max" in clean_df.columns

    def test_biometric_fields_present(self):
        clean_df, _ = clean(_make_df())
        assert "weight_kg" in clean_df.columns
        assert "height_cm" in clean_df.columns
        assert "bmi" in clean_df.columns
        assert "fat_percentage" in clean_df.columns
        assert "heart_rate_rest" in clean_df.columns
