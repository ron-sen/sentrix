"""add suitability_scores table

Revision ID: 4d8c3ee46e33
Revises: 10f3302a4404
Create Date: 2026-09-11 13:41:35.733730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4d8c3ee46e33'
down_revision: Union[str, Sequence[str], None] = '10f3302a4404'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('suitability_scores',
    sa.Column('asset_id', sa.BigInteger(), nullable=False),
    sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('suitability_score', sa.Numeric(), nullable=False),
    sa.Column('rsi_input', sa.Numeric(), nullable=False),
    sa.Column('ppo_input', sa.Numeric(), nullable=False),
    sa.Column('atr_input', sa.Numeric(), nullable=False),
    sa.CheckConstraint('suitability_score >= 0 AND suitability_score <= 100', name='ck_suitability_range'),
    sa.ForeignKeyConstraint(['asset_id'], ['assets.asset_id'], ),
    sa.PrimaryKeyConstraint('asset_id', 'timestamp')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('suitability_scores')
    # ### end Alembic commands ###