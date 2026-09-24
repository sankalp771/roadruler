"""Run the lightweight AI Phase 2 regression suite via ``python -m``."""

from pathlib import Path

import pytest


if __name__ == "__main__":
    test_dir = Path(__file__).parent
    raise SystemExit(
        pytest.main(
            [
                "-q",
                str(test_dir / "test_deduplication.py"),
                str(test_dir / "test_dedup_benchmark.py"),
                str(test_dir / "test_clustering.py"),
                str(test_dir / "test_seed_data.py"),
            ]
        )
    )
