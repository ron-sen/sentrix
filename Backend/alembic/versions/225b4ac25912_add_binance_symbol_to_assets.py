"""add binance_symbol to assets

Revision ID: 225b4ac25912
Revises: ae65a53d9046
Create Date: 2026-07-18 22:38:23.084181

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '225b4ac25912'
down_revision: Union[str, Sequence[str], None] = 'ae65a53d9046'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('assets', sa.Column('binance_symbol', sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column('assets', 'binance_symbol')