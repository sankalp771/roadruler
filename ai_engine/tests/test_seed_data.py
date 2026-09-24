from ai_engine.scripts.seed_data import AREAS, generate_records, _validate_image_template


def test_seed_generator_creates_150_deterministic_records_across_four_areas():
    first = generate_records(seed=17, image_url_template="https://media.example.org/phase2/{index}.jpg")
    second = generate_records(seed=17, image_url_template="https://media.example.org/phase2/{index}.jpg")
    assert len(first) == sum(area[3] for area in AREAS) == 150
    assert first == second
    assert {record["ward_id"] for record in first} == {f"SYNTHETIC_{area[0]}" for area in AREAS}
    assert all(0 <= record["severity_score"] <= 100 for record in first)
    assert all(record["latitude"] >= -90 and record["latitude"] <= 90 for record in first)
    assert all(record["longitude"] >= -180 and record["longitude"] <= 180 for record in first)


def test_seed_template_requires_https_and_index_placeholder():
    _validate_image_template("https://media.example.org/synthetic/{index}.jpg")
