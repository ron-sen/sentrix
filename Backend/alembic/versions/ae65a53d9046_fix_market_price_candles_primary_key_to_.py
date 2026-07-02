"""fix market_price_candles primary key to include asset_id

Revision ID: ae65a53d9046
Revises: 7efc01e6a5a2
Create Date: 2026-06-29 23:44:20.641870

"""
from typing import Sequence, Union

from alembic import op
 

# revision identifiers, used by Alembic.
revision: str = 'ae65a53d9046'
down_revision: Union[str, Sequence[str], None] = '7efc01e6a5a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('market_price_candles_pkey', 'market_price_candles', type_='primary')
    op.create_primary_key(
        'market_price_candles_pkey',
        'market_price_candles',
        ['asset_id', 'exchange', 'timeframe', 'candle_time']
    )


def downgrade() -> None:
    op.drop_constraint('market_price_candles_pkey', 'market_price_candles', type_='primary')
    op.create_primary_key(
        'market_price_candles_pkey',
        'market_price_candles',
        ['exchange', 'timeframe', 'candle_time']
    )
