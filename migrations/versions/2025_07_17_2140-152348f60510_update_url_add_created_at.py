"""update_url_add_created_at

Revision ID: 152348f60510
Revises: 72647c415257
Create Date: 2025-07-17 21:40:04.498006

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "152348f60510"
down_revision: str | Sequence[str] | None = "72647c415257"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("shortlink", "url", new_column_name="long_url")
    op.add_column("shortlink", sa.Column("created_at", sa.DateTime(), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("shortlink", "created_at")
    op.alter_column("shortlink", "long_url", new_column_name="url")
