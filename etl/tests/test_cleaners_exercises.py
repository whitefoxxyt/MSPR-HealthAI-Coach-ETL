import pandas as pd

from cleaners.exercises import clean


def _make_df(overrides=None):
    base = {
        "exerciseId": "ex001",
        "name": "Push Up",
        "bodyParts": ["chest"],
        "targetMuscles": ["pectorals"],
        "secondaryMuscles": ["triceps"],
        "equipments": ["body weight"],
        "instructions": ["Step 1", "Step 2"],
        "gifUrl": "https://example.com/pushup.gif",
    }
    if overrides:
        base.update(overrides)
    return pd.DataFrame([base])


class TestExercisesCleaner:
    def test_valid_row_accepted(self):
        clean_df, rejected_df = clean(_make_df())
        assert len(clean_df) == 1
        assert len(rejected_df) == 0

    def test_missing_exercise_id_rejected(self):
        clean_df, rejected_df = clean(_make_df({"exerciseId": ""}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1

    def test_missing_name_rejected(self):
        clean_df, rejected_df = clean(_make_df({"name": ""}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1

    def test_none_exercise_id_rejected(self):
        clean_df, rejected_df = clean(_make_df({"exerciseId": None}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1

    def test_instructions_joined(self):
        clean_df, _ = clean(_make_df({"instructions": ["Step 1", "Step 2", "Step 3"]}))
        assert clean_df.iloc[0]["instructions"] == "Step 1\nStep 2\nStep 3"

    def test_empty_instructions_is_none(self):
        clean_df, _ = clean(_make_df({"instructions": []}))
        assert clean_df.iloc[0]["instructions"] is None

    def test_fields_mapped(self):
        clean_df, _ = clean(_make_df())
        row = clean_df.iloc[0]
        assert row["external_id"] == "ex001"
        assert row["name"] == "Push Up"
        assert row["body_parts"] == ["chest"]
        assert row["target_muscles"] == ["pectorals"]
        assert row["secondary_muscles"] == ["triceps"]
        assert row["equipments"] == ["body weight"]
        assert row["gif_url"] == "https://example.com/pushup.gif"
