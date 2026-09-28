"""Add nullable ward assignment for authority queue filtering.

Revision ID: b750c3039f26
Revises: e41ac917f2b0
Create Date: 2026-09-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b750c3039f26"
down_revision: Union[str, Sequence[str], None] = "e41ac917f2b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("complaints", sa.Column("ward_id", sa.String(), nullable=True))
    op.create_index("ix_complaints_ward_id", "complaints", ["ward_id"])


def downgrade() -> None:
    op.drop_index("ix_complaints_ward_id", table_name="complaints")
    op.drop_column("complaints", "ward_id")
