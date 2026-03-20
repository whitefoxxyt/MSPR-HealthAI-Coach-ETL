from cleaners import nutrition as cleaner
from config import NUTRITION_CSV
from extractors import csv_extractor
from loaders.postgres_loader import TableConfig

PIPELINE = {
    "name": "nutrition_dataset",
    "extract": lambda: csv_extractor.extract(
        NUTRITION_CSV,
        {"Food_Item", "Calories (kcal)", "Protein (g)", "Carbohydrates (g)", "Fat (g)"},
        food_name_quirk=True,
    ),
    "clean": cleaner.clean,
    "tables": [
        TableConfig(
            table="nutrition_entries",
            columns=[
                "food_name",
                "category",
                "meal_type",
                "calories",
                "protein_g",
                "carbs_g",
                "fat_g",
                "fiber_g",
                "sugars_g",
                "sodium_mg",
                "cholesterol_mg",
                "water_ml",
                "source",
                "status",
            ],
            conflict_clause="ON CONFLICT (food_name, category, meal_type, source) DO NOTHING",
        ),
    ],
    "source": "NUTRITION_DATASET",
}
