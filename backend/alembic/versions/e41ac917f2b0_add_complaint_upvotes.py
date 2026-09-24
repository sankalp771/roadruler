"""Create unique complaint upvote records.

Revision ID: e41ac917f2b0
Revises: d9b2e6a401cf
Create Date: 2026-09-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e41ac917f2b0"
down_revision: Union[str, Sequence[str], None] = "d9b2e6a401cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "complaint_upvotes",
        sa.Column("complaint_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["complaint_id"], ["complaints.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("complaint_id", "user_id"),
    )


def downgrade() -> None:
    op.drop_table("complaint_upvotes")
