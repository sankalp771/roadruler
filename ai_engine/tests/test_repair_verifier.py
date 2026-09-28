import pytest

from ai_engine.repair_verifier import verify_repair


BOX = {"bbox_normalized": [0.2, 0.2, 0.5, 0.5]}


def test_verifier_confirms_cleared_damage_in_same_scene():
    detector_results = iter([[BOX], []])
    result = verify_repair(
        b"before",
        b"after",
        detector=lambda _image: next(detector_results),
        embedder=lambda _image: [1.0, 0.0, 0.0],
    )

    assert result == {
        "status": "REPAIR_VERIFIED",
        "reason": "DAMAGE_CLEARED_AND_SCENE_MATCHED",
        "similarity": 1.0,
        "remaining_damage_count": 0,
    }


def test_verifier_rejects_damage_still_present_in_original_area():
    detector_results = iter([[BOX], [{"bbox_normalized": [0.25, 0.25, 0.45, 0.45]}]])
    result = verify_repair(
        b"before",
        b"after",
        detector=lambda _image: next(detector_results),
        embedder=lambda _image: pytest.fail("Embedding should not run while damage remains"),
    )

    assert result["status"] == "REPAIR_NOT_VERIFIED"
    assert result["reason"] == "DAMAGE_REMAINS_IN_ORIGINAL_AREA"


def test_verifier_requires_scene_similarity_and_original_damage():
    detector_results = iter([[BOX], []])
    low_similarity = verify_repair(
        b"before",
        b"after",
        detector=lambda _image: next(detector_results),
        embedder=lambda image: [1.0, 0.0] if image == b"before" else [0.0, 1.0],
    )
    no_original = verify_repair(b"before", b"after", detector=lambda _image: [], embedder=lambda _image: [1, 0])

    assert low_similarity["status"] == "NEEDS_REVIEW"
    assert low_similarity["reason"] == "SCENE_SIMILARITY_TOO_LOW"
    assert no_original["reason"] == "ORIGINAL_DAMAGE_NOT_DETECTED"


def test_verifier_validates_image_bytes_boxes_and_thresholds():
    with pytest.raises(ValueError, match="Both before and after"):
        verify_repair(b"", b"after", detector=lambda _image: [], embedder=lambda _image: [1])
    with pytest.raises(ValueError, match="normalized"):
        verify_repair(
            b"before", b"after",
            detector=lambda _image: [{"bbox_normalized": [-1, 0, 1, 1]}],
            embedder=lambda _image: [1],
        )
