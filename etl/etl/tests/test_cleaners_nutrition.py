import pandas as pd

from cleaners.nutrition import clean


def _make_df(overrides=None):
    base = {
        "Food_Item": "Apple",
        "Category": "Fruit",
        "Meal_Type": "Snack",
        "Calories (kcal)": "95",
        "Protein (g)": "0.5",
        "Carbohydrates (g)": "25",
        "Fat (g)": "0.3",
        "Fiber (g)": "4.4",
        "Sugars (g)": "19",
        "Sodium (mg)": "1",
        "Cholesterol (mg)": "0",
        "Water_Intake (ml)": "200",
    }
    if overrides:
        base.update(overrides)
    return pd.DataFrame([base])


class TestNutritionCleaner:
    def test_valid_row_accepted(self):
        clean_df, rejected_df = clean(_make_df())
        assert len(clean_df) == 1
        assert len(rejected_df) == 0
        assert clean_df.iloc[0]["food_name"] == "Apple"
        assert clean_df.iloc[0]["calories"] == 95.0

    def test_status_nettoye(self):
        clean_df, _ = clean(_make_df())
        assert clean_df.iloc[0]["status"] == "NETTOYE"

    def test_missing_food_item_rejected(self):
        clean_df, rejected_df = clean(_make_df({"Food_Item": ""}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
        assert "food_name" in rejected_df.iloc[0]["reason"]

    def test_calories_above_bound_rejected(self):
        clean_df, rejected_df = clean(_make_df({"Calories (kcal)": "15000"}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
        assert "calories" in rejected_df.iloc[0]["reason"]

    def test_calories_below_bound_rejected(self):
        clean_df, rejected_df = clean(_make_df({"Calories (kcal)": "-5"}))
        assert len(clean_df) == 0
        assert len(rejected_df) == 1

    def test_calories_at_zero_accepted(self):
        clean_df, _ = clean(_make_df({"Calories (kcal)": "0"}))
        assert len(clean_df) == 1
        assert clean_df.iloc[0]["calories"] == 0.0

    def test_calories_at_upper_bound_accepted(self):
        clean_df, _ = clean(_make_df({"Calories (kcal)": "10000"}))
        assert len(clean_df) == 1
        assert clean_df.iloc[0]["calories"] == 10_000.0

    def test_negative_protein_clamped(self):
        clean_df, _ = clean(_make_df({"Protein (g)": "-5"}))
        assert len(clean_df) == 1
        assert clean_df.iloc[0]["protein_g"] == 0.0

    def test_negative_carbs_clamped(self):
        clean_df, _ = clean(_make_df({"Carbohydrates (g)": "-2"}))
        assert len(clean_df) == 1
        assert clean_df.iloc[0]["carbs_g"] == 0.0

    def test_negative_fat_clamped(self):
        clean_df, _ = clean(_make_df({"Fat (g)": "-1"}))
        assert len(clean_df) == 1
        assert clean_df.iloc[0]["fat_g"] == 0.0

    def test_none_calories_passes(self):
        clean_df, _ = clean(_make_df({"Calories (kcal)": ""}))
        assert len(clean_df) == 1
        assert pd.isna(clean_df.iloc[0]["calories"])

    def test_multiple_rows(self):
        df = pd.concat(
            [_make_df(), _make_df({"Food_Item": ""}), _make_df()],
            ignore_index=True,
        )
        clean_df, rejected_df = clean(df)
        assert len(clean_df) == 2
        assert len(rejected_df) == 1
