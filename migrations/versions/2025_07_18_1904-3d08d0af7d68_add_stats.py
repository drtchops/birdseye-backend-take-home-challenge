"""add_stats

Revision ID: 3d08d0af7d68
Revises: 152348f60510
Create Date: 2025-07-18 19:04:14.252712

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3d08d0af7d68"
down_revision: str | Sequence[str] | None = "152348f60510"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "shortlinkstat",
        sa.Column("shortlink_id", sa.Uuid(), nullable=False),
        sa.Column("visits", sa.Integer(), nullable=False),
        sa.Column("last_visit", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["shortlink_id"],
            ["shortlink.id"],
        ),
        sa.PrimaryKeyConstraint("shortlink_id"),
    )
    op.create_index(op.f("ix_shortlinkstat_last_visit"), "shortlinkstat", ["last_visit"], unique=False)
    op.create_index(op.f("ix_shortlinkstat_visits"), "shortlinkstat", ["visits"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_shortlinkstat_visits"), table_name="shortlinkstat")
    op.drop_index(op.f("ix_shortlinkstat_last_visit"), table_name="shortlinkstat")
    op.drop_table("shortlinkstat")
