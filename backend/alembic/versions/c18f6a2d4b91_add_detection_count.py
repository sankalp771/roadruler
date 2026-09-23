"""Persist AI damage detection counts.

Revision ID: c18f6a2d4b91
Revises: b3d1a9e42c17
Create Date: 2026-09-23 17:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c18f6a2d4b91"
down_revision: Union[str, Sequence[str], None] = "b3d1a9e42c17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "complaints",
        sa.Column("detections_count", sa.Integer(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("complaints", "detections_count")
