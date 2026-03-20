from cleaners import diet_recommendations as cleaner
from config import DIET_RECOMMENDATIONS_CSV
from extractors import csv_extractor
from loaders.postgres_loader import TableConfig

PIPELINE = {
    "name": "diet_recommendations",
    "extract": lambda: csv_extractor.extract(
        DIET_RECOMMENDATIONS_CSV,
        {"Patient_ID", "Diet_Recommendation", "Disease_Type", "Weight_kg", "Height_cm", "BMI"},
    ),
    "clean": cleaner.clean,
    "tables": [
        TableConfig(
            table="diet_recommendations",
            columns=[
                "external_patient_id",
                "age",
                "gender",
                "weight_kg",
                "height_cm",
                "bmi",
                "disease_type",
                "severity",
                "physical_activity_level",
                "daily_caloric_intake",
                "cholesterol_mg_dl",
                "blood_pressure_mmhg",
                "glucose_mg_dl",
                "dietary_restrictions",
                "allergies",
                "preferred_cuisine",
                "weekly_exercise_hours",
                "adherence_to_diet_plan",
                "nutrient_imbalance_score",
                "diet_recommendation",
                "source",
            ],
            conflict_clause="ON CONFLICT (external_patient_id) DO NOTHING",
        ),
    ],
    "source": "DIET_RECOMMENDATIONS",
}
