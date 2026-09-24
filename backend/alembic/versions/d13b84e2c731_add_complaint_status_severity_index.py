"""Index authority queue status and severity filters.

Revision ID: d13b84e2c731
Revises: c12a71f9d460
Create Date: 2026-09-23
"""
from typing import Sequence, Union

from alembic import op

revision: str = "d13b84e2c731"
down_revision: Union[str, Sequence[str], None] = "c12a71f9d460"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_complaints_status_severity",
        "complaints",
        ["status", "severity_level"],
    )


def downgrade() -> None:
    op.drop_index("idx_complaints_status_severity", table_name="complaints")
