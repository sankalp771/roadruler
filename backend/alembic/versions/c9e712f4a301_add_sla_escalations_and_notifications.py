"""Add SLA escalation state and citizen notification records.

Revision ID: c9e712f4a301
Revises: f3a95d1b7c42
Create Date: 2026-09-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9e712f4a301"
down_revision: Union[str, Sequence[str], None] = "f3a95d1b7c42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("complaints", sa.Column("escalation_level", sa.Integer(), nullable=False, server_default="0"))
    op.create_table(
        "notifications",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("complaint_id", sa.String(), sa.ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_complaint_id", "notifications", ["complaint_id"])


def downgrade() -> None:
    op.drop_index("ix_notifications_complaint_id", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_column("complaints", "escalation_level")
