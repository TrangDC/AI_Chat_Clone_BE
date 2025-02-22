"""Add cascade delete to session-message relationship

Revision ID: 699830176547
Revises: 97f614ae231f
Create Date: 2025-02-22 15:14:29.460455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '699830176547'
down_revision: Union[str, None] = '97f614ae231f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
