"""Add polygon-based complaint routing and department ownership.

Revision ID: f3a95d1b7c42
Revises: b750c3039f26
Create Date: 2026-09-29
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


revision: str = "f3a95d1b7c42"
down_revision: Union[str, Sequence[str], None] = "b750c3039f26"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("complaints", sa.Column("department_name", sa.String(), nullable=True))
    op.create_table(
        "ward_boundaries",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("department_name", sa.String(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("geom", Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False),
    )
    op.create_index("idx_ward_boundaries_geom", "ward_boundaries", ["geom"], postgresql_using="gist")


def downgrade() -> None:
    op.drop_index("idx_ward_boundaries_geom", table_name="ward_boundaries")
    op.drop_table("ward_boundaries")
    op.drop_column("complaints", "department_name")
