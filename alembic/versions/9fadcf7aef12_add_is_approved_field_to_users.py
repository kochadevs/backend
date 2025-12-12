"""add_is_approved_field_to_users

Revision ID: 9fadcf7aef12
Revises: 665hhe7hu66
Create Date: 2025-12-12 01:50:33.558068

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9fadcf7aef12'
down_revision: Union[str, Sequence[str], None] = '665hhe7hu66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add is_approved column to users table
    op.add_column('users', sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove is_approved column from users table
    op.drop_column('users', 'is_approved')
