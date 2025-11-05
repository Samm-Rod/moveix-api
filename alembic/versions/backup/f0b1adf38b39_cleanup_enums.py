"""cleanup_enums

Revision ID: f0b1adf38b39
Revises: a526cf623cc4
Create Date: 2025-09-22 02:33:37.570508

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0b1adf38b39'
down_revision: Union[str, Sequence[str], None] = 'a526cf623cc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
