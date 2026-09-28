"""Persist per-region AI detection details.

Revision ID: a72d4c9e5f10
Revises: c18f6a2d4b91
Create Date: 2026-09-23 18:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a72d4c9e5f10"
down_revision: Union[str, Sequence[str], None] = "c18f6a2d4b91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "complaints",
        sa.Column("detection_details", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("complaints", "detection_details")
