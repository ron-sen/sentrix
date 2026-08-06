"""baseline schema

Revision ID: a4b75dfe8f80
Revises: 225b4ac25912
Create Date: 2026-08-06 19:47:22.948772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a4b75dfe8f80'
down_revision: Union[str, Sequence[str], None] = '225b4ac25912'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass