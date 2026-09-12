"""add ppo to indicator_values

Revision ID: 10f3302a4404
Revises: 8da24be32528
Create Date: 2026-09-09 11:29:45.479429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '10f3302a4404'
down_revision: Union[str, Sequence[str], None] = '8da24be32528'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('indicator_values', sa.Column('ppo', sa.Numeric(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('indicator_values', 'ppo')
    # ### end Alembic commands ###