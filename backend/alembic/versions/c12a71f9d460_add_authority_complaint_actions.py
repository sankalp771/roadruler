"""Add immutable authority status action records.

Revision ID: c12a71f9d460
Revises: b750c3039f26
Create Date: 2026-09-23
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c12a71f9d460"
down_revision: Union[str, Sequence[str], None] = "b750c3039f26"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "complaint_actions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("complaint_id", sa.String(), nullable=False),
        sa.Column("actor_user_id", sa.String(), nullable=False),
        sa.Column("previous_status", sa.String(), nullable=False),
        sa.Column("new_status", sa.String(), nullable=False),
        sa.Column("contractor_name", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("resolution_image_url", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["complaint_id"], ["complaints.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_complaint_actions_complaint_id", "complaint_actions", ["complaint_id"])


def downgrade() -> None:
    op.drop_index("ix_complaint_actions_complaint_id", table_name="complaint_actions")
    op.drop_table("complaint_actions")
