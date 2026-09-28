"""Merge authority-action and routing/SLA schema branches.

Revision ID: f85e93a7c210
Revises: d13b84e2c731, c9e712f4a301
Create Date: 2026-09-29
"""
from typing import Sequence, Union


revision: str = "f85e93a7c210"
down_revision: Union[str, Sequence[str], None] = ("d13b84e2c731", "c9e712f4a301")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
