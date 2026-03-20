import json
import textwrap

import pytest

from extractors import csv_extractor, json_extractor


def test_csv_extract_standard(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("name,calories\nApple,52\nBanana,89\n")

    df = csv_extractor.extract(str(f))

    assert list(df.columns) == ["name", "calories"]
    assert len(df) == 2
    assert df.iloc[0]["name"] == "Apple"


def test_csv_extract_missing_columns_raises(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text("name,calories\nApple,52\n")

    with pytest.raises(ValueError, match="Colonnes manquantes"):
        csv_extractor.extract(str(f), required_columns={"name", "protein"})


def test_csv_extract_multiple_paths(tmp_path):
    f1 = tmp_path / "a.csv"
    f1.write_text("name,val\nA,1\n")
    f2 = tmp_path / "b.csv"
    f2.write_text("name,val\nB,2\n")

    df = csv_extractor.extract([str(f1), str(f2)])

    assert len(df) == 2
    assert list(df["name"]) == ["A", "B"]


def test_csv_extract_food_quirk_handles_comma_in_name(tmp_path):
    """Les noms contenant des virgules doivent être reconstitués."""
    f = tmp_path / "nutrition.csv"
    f.write_text(
        textwrap.dedent("""\
        food_name,calories,protein
        Apple,52,0.3
        Apple Red Delicious,80,0.4
        Beans,Black,120,7.5
    """)
    )

    df = csv_extractor.extract(str(f), food_name_quirk=True)

    assert len(df) == 3
    assert df.iloc[2]["food_name"] == "Beans,Black"
    assert df.iloc[2]["calories"] == "120"


def test_csv_extract_food_quirk_missing_columns_raises(tmp_path):
    f = tmp_path / "nutrition.csv"
    f.write_text("food_name,calories\nApple,52\n")

    with pytest.raises(ValueError, match="Colonnes manquantes"):
        csv_extractor.extract(
            str(f), required_columns={"food_name", "protein"}, food_name_quirk=True
        )


def test_json_extract(tmp_path):
    f = tmp_path / "data.json"
    f.write_text(json.dumps([{"id": 1, "name": "Push-up"}, {"id": 2, "name": "Squat"}]))

    df = json_extractor.extract(str(f))

    assert len(df) == 2
    assert list(df.columns) == ["id", "name"]


def test_json_extract_non_list_raises(tmp_path):
    f = tmp_path / "data.json"
    f.write_text(json.dumps({"key": "value"}))

    with pytest.raises(ValueError, match="liste attendue"):
        json_extractor.extract(str(f))


def test_json_extract_missing_columns_raises(tmp_path):
    f = tmp_path / "data.json"
    f.write_text(json.dumps([{"id": 1}]))

    with pytest.raises(ValueError, match="Colonnes manquantes"):
        json_extractor.extract(str(f), required_columns={"id", "name"})
