"""Persist visual embeddings and duplicate links for complaints.

Revision ID: d9b2e6a401cf
Revises: a72d4c9e5f10
Create Date: 2026-09-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d9b2e6a401cf"
down_revision: Union[str, Sequence[str], None] = "a72d4c9e5f10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("complaints", sa.Column("visual_embedding", sa.JSON(), nullable=True))
    op.add_column(
        "complaints",
        sa.Column(
            "duplicate_of_id",
            sa.String(),
            sa.ForeignKey("complaints.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("complaints", "duplicate_of_id")
    op.drop_column("complaints", "visual_embedding")
