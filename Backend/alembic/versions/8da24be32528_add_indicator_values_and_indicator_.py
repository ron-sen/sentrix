"""add indicator_values and indicator_signals

Revision ID: 8da24be32528
Revises: 9841f71369f4
Create Date: 2026-09-01 19:55:54.187328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8da24be32528'
down_revision: Union[str, Sequence[str], None] = '9841f71369f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('indicator_signals',
    sa.Column('asset_id', sa.BigInteger(), nullable=False),
    sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('sma_slope', sa.String(length=10), nullable=False),
    sa.Column('ema_slope', sa.String(length=10), nullable=False),
    sa.Column('rsi_status', sa.String(length=15), nullable=False),
    sa.Column('macd_crossover', sa.String(length=10), nullable=False),
    sa.Column('macd_hist_direction', sa.String(length=15), nullable=False),
    sa.Column('bb_status', sa.String(length=10), nullable=False),
    sa.Column('atr_vol_regime', sa.String(length=10), nullable=False),
    sa.Column('adx_trend_strength', sa.String(length=15), nullable=False),
    sa.Column('adx_trend_direction', sa.String(length=15), nullable=False),
    sa.Column('obv_trend', sa.String(length=15), nullable=False),
    sa.Column('vwap_position', sa.String(length=15), nullable=False),
    sa.Column('vwap_deviation_pct', sa.Numeric(), nullable=False),
    sa.Column('stoch_status', sa.String(length=15), nullable=False),
    sa.Column('stoch_crossover', sa.String(length=15), nullable=False),
    sa.CheckConstraint("adx_trend_direction IN ('bullish','bearish','none')", name='ck_adx_direction'),
    sa.CheckConstraint("adx_trend_strength IN ('weak','strong','very_strong')", name='ck_adx_strength'),
    sa.CheckConstraint("atr_vol_regime IN ('high','low','normal')", name='ck_atr_vol_regime'),
    sa.CheckConstraint("bb_status IN ('overbought','oversold','squeeze','normal')", name='ck_bb_status'),
    sa.CheckConstraint("ema_slope IN ('rising','falling','flat')", name='ck_ema_slope'),
    sa.CheckConstraint("macd_crossover IN ('bullish','bearish','none')", name='ck_macd_crossover'),
    sa.CheckConstraint("macd_hist_direction IN ('expanding','contracting','flat')", name='ck_macd_hist_dir'),
    sa.CheckConstraint("obv_trend IN ('rising','falling','flat')", name='ck_obv_trend'),
    sa.CheckConstraint("rsi_status IN ('overbought','oversold','neutral')", name='ck_rsi_status'),
    sa.CheckConstraint("sma_slope IN ('rising','falling','flat')", name='ck_sma_slope'),
    sa.CheckConstraint("stoch_crossover IN ('bullish','bearish','none')", name='ck_stoch_crossover'),
    sa.CheckConstraint("stoch_status IN ('overbought','oversold','neutral')", name='ck_stoch_status'),
    sa.CheckConstraint("vwap_position IN ('above','below','at')", name='ck_vwap_position'),
    sa.ForeignKeyConstraint(['asset_id'], ['assets.asset_id'], ),
    sa.PrimaryKeyConstraint('asset_id', 'timestamp')
    )
    op.create_table('indicator_values',
    sa.Column('asset_id', sa.BigInteger(), nullable=False),
    sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('sma', sa.Numeric(), nullable=False),
    sa.Column('ema', sa.Numeric(), nullable=False),
    sa.Column('rsi', sa.Numeric(), nullable=False),
    sa.Column('macd_line', sa.Numeric(), nullable=False),
    sa.Column('macd_signal', sa.Numeric(), nullable=False),
    sa.Column('macd_hist', sa.Numeric(), nullable=False),
    sa.Column('bb_upper', sa.Numeric(), nullable=False),
    sa.Column('bb_middle', sa.Numeric(), nullable=False),
    sa.Column('bb_lower', sa.Numeric(), nullable=False),
    sa.Column('bb_percent_b', sa.Numeric(), nullable=False),
    sa.Column('bb_bandwidth', sa.Numeric(), nullable=False),
    sa.Column('atr', sa.Numeric(), nullable=False),
    sa.Column('adx', sa.Numeric(), nullable=False),
    sa.Column('plus_di', sa.Numeric(), nullable=False),
    sa.Column('minus_di', sa.Numeric(), nullable=False),
    sa.Column('obv', sa.BigInteger(), nullable=False),
    sa.Column('vwap', sa.Numeric(), nullable=False),
    sa.Column('stoch_k', sa.Numeric(), nullable=False),
    sa.Column('stoch_d', sa.Numeric(), nullable=False),
    sa.CheckConstraint('adx >= 0 AND adx <= 100', name='ck_adx_range'),
    sa.CheckConstraint('minus_di >= 0 AND minus_di <= 100', name='ck_minus_di_range'),
    sa.CheckConstraint('plus_di >= 0 AND plus_di <= 100', name='ck_plus_di_range'),
    sa.CheckConstraint('rsi >= 0 AND rsi <= 100', name='ck_rsi_range'),
    sa.CheckConstraint('stoch_d >= 0 AND stoch_d <= 100', name='ck_stoch_d_range'),
    sa.CheckConstraint('stoch_k >= 0 AND stoch_k <= 100', name='ck_stoch_k_range'),
    sa.ForeignKeyConstraint(['asset_id'], ['assets.asset_id'], ),
    sa.PrimaryKeyConstraint('asset_id', 'timestamp')
    )
    # ### end Alembic commands ###