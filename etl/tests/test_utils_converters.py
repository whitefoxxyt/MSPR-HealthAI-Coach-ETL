from utils.converters import str_or_none, to_float, to_int


class TestToFloat:
    def test_normal_float(self):
        assert to_float(3.14) == 3.14

    def test_string_float(self):
        assert to_float("3.14") == 3.14

    def test_int_value(self):
        assert to_float(42) == 42.0

    def test_none_returns_none(self):
        assert to_float(None) is None

    def test_empty_string_returns_none(self):
        assert to_float("") is None

    def test_whitespace_string_returns_none(self):
        assert to_float("  ") is None

    def test_nan_returns_none(self):
        assert to_float(float("nan")) is None

    def test_invalid_string_returns_none(self):
        assert to_float("abc") is None

    def test_zero(self):
        assert to_float(0) == 0.0

    def test_negative(self):
        assert to_float(-5.5) == -5.5


class TestToInt:
    def test_normal_int(self):
        assert to_int(42) == 42

    def test_float_rounds(self):
        assert to_int(3.7) == 4

    def test_string_int(self):
        assert to_int("42") == 42

    def test_none_returns_none(self):
        assert to_int(None) is None

    def test_zero(self):
        assert to_int(0) == 0

    def test_negative_rounds(self):
        assert to_int(-2.3) == -2


class TestStrOrNone:
    def test_normal_string(self):
        assert str_or_none("hello") == "hello"

    def test_none_returns_none(self):
        assert str_or_none(None) is None

    def test_empty_string_returns_none(self):
        assert str_or_none("") is None

    def test_none_literal_returns_none(self):
        assert str_or_none("None") is None

    def test_none_case_insensitive(self):
        assert str_or_none("NONE") is None
        assert str_or_none("none") is None

    def test_whitespace_stripped(self):
        assert str_or_none("  hello  ") == "hello"
