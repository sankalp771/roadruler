from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_day15_and_day16_migrations_are_in_single_head_chain():
    backend_root = Path(__file__).resolve().parents[1]
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "alembic"))
    script = ScriptDirectory.from_config(config)

    assert script.get_heads() == ["f85e93a7c210"]
    merge_revision = script.get_revision("f85e93a7c210")
    assert set(merge_revision.down_revision) == {"d13b84e2c731", "c9e712f4a301"}
    assert script.get_revision("f3a95d1b7c42") is not None
    assert script.get_revision("c9e712f4a301") is not None
    assert script.get_revision("d13b84e2c731") is not None
