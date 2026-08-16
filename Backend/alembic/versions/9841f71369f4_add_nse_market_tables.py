"""add nse market tables

Revision ID: 9841f71369f4
Revises: a4b75dfe8f80
Create Date: 2026-08-16 20:24:33.353671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9841f71369f4'
down_revision: Union[str, Sequence[str], None] = 'a4b75dfe8f80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('market_breadth',
    sa.Column('breadth_id', sa.Integer(), nullable=False),
    sa.Column('exchange', sa.String(length=16), nullable=False),
    sa.Column('session_date', sa.Date(), nullable=False),
    sa.Column('advances', sa.Integer(), nullable=False),
    sa.Column('declines', sa.Integer(), nullable=False),
    sa.Column('unchanged', sa.Integer(), nullable=False),
    sa.Column('total', sa.Integer(), nullable=False),
    sa.Column('advance_decline_ratio', sa.Numeric(precision=10, scale=4), nullable=False),
    sa.Column('put_call_ratio', sa.Numeric(precision=10, scale=4), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.CheckConstraint("exchange IN ('NSE', 'BSE')", name='chk_breadth_exchange'),
    sa.PrimaryKeyConstraint('breadth_id'),
    sa.UniqueConstraint('exchange', 'session_date', name='uq_breadth_exchange_date')
    )
    op.create_table('marketinstruments',
    sa.Column('instrument_id', sa.Integer(), nullable=False),
    sa.Column('symbol', sa.String(length=32), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('instrument_type', sa.String(length=24), nullable=False),
    sa.Column('exchange', sa.String(length=16), nullable=False),
    sa.Column('nse_symbol', sa.String(length=32), nullable=True),
    sa.Column('isin', sa.String(length=12), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.CheckConstraint("exchange IN ('NSE' , 'BSE')"),
    sa.CheckConstraint("instrument_type IN('INDEX' , 'EQUITY')", name='chk_instrument_type'),
    sa.PrimaryKeyConstraint('instrument_id'),
    sa.UniqueConstraint('symbol')
    )
    op.create_table('nsepricecandles',
    sa.Column('instrument_id', sa.Integer(), nullable=False),
    sa.Column('exchange', sa.String(length=16), nullable=False),
    sa.Column('timeframe', sa.String(length=12), nullable=False),
    sa.Column('candle_time', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('open_price', sa.Numeric(precision=28, scale=10), nullable=False),
    sa.Column('close_price', sa.Numeric(precision=28, scale=10), nullable=False),
    sa.Column('high_price', sa.Numeric(precision=28, scale=10), nullable=False),
    sa.Column('low_price', sa.Numeric(precision=28, scale=10), nullable=False),
    sa.Column('volume', sa.Numeric(precision=38, scale=18), nullable=True),
    sa.Column('quote_volume', sa.Numeric(precision=38, scale=10), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.CheckConstraint("timeframe IN('1m', '5m', '15m', '1h', '1d')", name='chk_timeframe'),
    sa.ForeignKeyConstraint(['instrument_id'], ['marketinstruments.instrument_id'], ),
    sa.PrimaryKeyConstraint('instrument_id', 'exchange', 'timeframe', 'candle_time')
    )


def downgrade() -> None:
    op.drop_table('nsepricecandles')
    op.drop_table('marketinstruments')
    op.drop_table('market_breadth')