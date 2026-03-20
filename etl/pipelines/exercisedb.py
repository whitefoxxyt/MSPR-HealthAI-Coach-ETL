from cleaners import exercises as cleaner
from config import EXERCISES_JSON
from extractors import json_extractor
from loaders.postgres_loader import TableConfig

PIPELINE = {
    "name": "exercisedb",
    "extract": lambda: json_extractor.extract(EXERCISES_JSON),
    "clean": cleaner.clean,
    "tables": [
        TableConfig(
            table="exercises",
            columns=[
                "external_id",
                "name",
                "body_parts",
                "target_muscles",
                "secondary_muscles",
                "equipments",
                "instructions",
                "gif_url",
            ],
            conflict_clause="ON CONFLICT (external_id) DO NOTHING",
        ),
    ],
    "source": None,
}
