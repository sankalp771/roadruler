import numpy as np
import pytest

from ai_engine.deduplication import check_duplicate, compute_cosine_similarity


def test_cosine_similarity_matches_identical_embeddings():
    assert compute_cosine_similarity([1, 2, 3], [1, 2, 3]) == pytest.approx(1.0)


def test_cosine_similarity_returns_zero_for_zero_vector():
    assert compute_cosine_similarity([0, 0], [1, 1]) == 0.0


def test_cosine_similarity_rejects_mismatched_dimensions():
    with pytest.raises(ValueError, match="same dimensions"):
        compute_cosine_similarity([1, 2], [1, 2, 3])


def test_check_duplicate_returns_best_candidate_at_threshold():
    is_duplicate, complaint_id, similarity = check_duplicate(
        [1, 0], [("similar", [0.99, 0.01]), ("different", [0, 1])]
    )

    assert is_duplicate is True
    assert complaint_id == "similar"
    assert similarity > 0.99


def test_check_duplicate_handles_no_candidates():
    assert check_duplicate(np.array([1.0, 0.0]), []) == (False, None, 0.0)


def test_check_duplicate_rejects_invalid_threshold():
    with pytest.raises(ValueError, match="threshold"):
        check_duplicate([1, 0], [], threshold=1.1)
