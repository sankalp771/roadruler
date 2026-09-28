"""Add ai_category column for AI enrichment (Day 5)

Revision ID: b3d1a9e42c17
Revises: 7fed6b8c9e2f
Create Date: 2026-08-14 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3d1a9e42c17'
down_revision: Union[str, Sequence[str], None] = '7fed6b8c9e2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('complaints', sa.Column('ai_category', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('complaints', 'ai_category')
