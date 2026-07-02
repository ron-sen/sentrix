"""track market_price_candles table

Revision ID: 7efc01e6a5a2
Revises: 891cdd5a5445
Create Date: 2026-06-24 00:22:58.932807

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7efc01e6a5a2'
down_revision: Union[str, Sequence[str], None] = '891cdd5a5445'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass