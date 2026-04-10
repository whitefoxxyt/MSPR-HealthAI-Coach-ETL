from cleaners import gym_tracking as cleaner
from config import GYM_TRACKING_CSVS
from extractors import csv_extractor
from loaders.postgres_loader import TableConfig

PIPELINE = {
    "name": "gym_tracking",
    "extract": lambda: csv_extractor.extract(
        GYM_TRACKING_CSVS,
        {
            "Workout_Type",
            "Session_Duration (hours)",
            "Calories_Burned",
            "Weight (kg)",
            "Height (m)",
            "BMI",
            "Avg_BPM",
            "Max_BPM",
            "Resting_BPM",
        },
    ),
    "clean": cleaner.clean,
    "tables": [
        TableConfig(
            table="exercise_entries",
            columns=[
                "workout_type",
                "duration_min",
                "calories_burned",
                "heart_rate_avg",
                "heart_rate_max",
                "source",
                "status",
            ],
            conflict_clause=(
                "ON CONFLICT (workout_type, duration_min, calories_burned, "
                "heart_rate_avg, heart_rate_max, source) DO NOTHING"
            ),
        ),
        TableConfig(
            table="biometric_entries",
            columns=[
                "weight_kg",
                "height_cm",
                "bmi",
                "fat_percentage",
                "heart_rate_rest",
                "heart_rate_avg",
                "heart_rate_max",
                "age",
                "gender",
                "experience_level",
                "source",
                "status",
            ],
            conflict_clause=(
                "ON CONFLICT (weight_kg, height_cm, bmi, fat_percentage, "
                "heart_rate_rest, heart_rate_avg, heart_rate_max, source) DO NOTHING"
            ),
        ),
    ],
    "source": "GYM_TRACKING",
}
