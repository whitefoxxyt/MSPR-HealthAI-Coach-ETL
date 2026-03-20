import pandas as pd

from utils.validators import BOUNDS, validate_bounds, validate_range


class TestValidateRange:
    def test_within_bounds(self):
        val, reason = validate_range(500, 0, 10_000, "calories")
        assert val == 500
        assert reason is None

    def test_at_lower_bound(self):
        val, reason = validate_range(0, 0, 10_000, "calories")
        assert val == 0
        assert reason is None

    def test_at_upper_bound(self):
        val, reason = validate_range(10_000, 0, 10_000, "calories")
        assert val == 10_000
        assert reason is None

    def test_below_lower_bound(self):
        val, reason = validate_range(-1, 0, 10_000, "calories")
        assert val is None
        assert reason is not None
        assert "calories" in reason

    def test_above_upper_bound(self):
        val, reason = validate_range(10_001, 0, 10_000, "calories")
        assert val is None
        assert reason is not None

    def test_none_passthrough(self):
        val, reason = validate_range(None, 0, 10_000, "calories")
        assert val is None
        assert reason is None

    def test_reason_contains_value(self):
        _, reason = validate_range(999, 0, 100, "test_field")
        assert "999" in reason
        assert "test_field" in reason


class TestBoundsConstants:
    def test_all_bounds_defined(self):
        expected = {
            "calories",
            "weight_kg",
            "height_cm",
            "bmi",
            "heart_rate",
            "fat_percentage",
            "duration_min",
        }
        assert set(BOUNDS.keys()) == expected

    def test_bounds_are_tuples_of_two(self):
        for key, bounds in BOUNDS.items():
            assert len(bounds) == 2, f"{key} devrait avoir 2 éléments"
            assert bounds[0] < bounds[1], f"{key} min devrait être inférieur à max"


class TestValidateBounds:
    def test_within_bounds(self):
        df = pd.DataFrame({"calories": [500.0]})
        result = validate_bounds(df, "calories", "calories")
        assert bool(result.iloc[0]) is True

    def test_below_lower_bound(self):
        df = pd.DataFrame({"calories": [-1.0]})
        result = validate_bounds(df, "calories", "calories")
        assert bool(result.iloc[0]) is False

    def test_above_upper_bound(self):
        df = pd.DataFrame({"calories": [10_001.0]})
        result = validate_bounds(df, "calories", "calories")
        assert bool(result.iloc[0]) is False

    def test_nan_passes(self):
        df = pd.DataFrame({"calories": [float("nan")]})
        result = validate_bounds(df, "calories", "calories")
        assert bool(result.iloc[0]) is True

    def test_at_bounds(self):
        df = pd.DataFrame({"calories": [0.0, 10_000.0]})
        result = validate_bounds(df, "calories", "calories")
        assert bool(result.iloc[0]) is True
        assert bool(result.iloc[1]) is True

    def test_multiple_rows(self):
        df = pd.DataFrame({"weight_kg": [80.0, 5.0, 150.0, float("nan")]})
        result = validate_bounds(df, "weight_kg", "weight_kg")
        assert list(result) == [True, False, True, True]
