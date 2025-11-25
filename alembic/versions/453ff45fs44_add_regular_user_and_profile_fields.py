"""add regular user type and profile fields

Revision ID: 453ff45fs44
Revises: 65918e7307eb
Create Date: 2025-11-24 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '453ff45fs44'
down_revision: Union[str, Sequence[str], None] = '65918e7307eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add 'regular' value to UserTypeEnum
    op.execute("ALTER TYPE usertypeenum ADD VALUE IF NOT EXISTS 'regular'")

    # Add new columns to users table
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('users', sa.Column('cover_photo', sa.String(), nullable=True))
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('social_links', sa.JSON(), nullable=True))
    op.add_column('users', sa.Column('availability', sa.JSON(), nullable=True))

    # Make gender and nationality nullable for step-based signup
    op.alter_column('users', 'gender', existing_type=sa.String(), nullable=True)
    op.alter_column('users', 'nationality', existing_type=sa.String(), nullable=True)

    # Create email_verifications table
    op.create_table(
        'email_verifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('verification_token', sa.String(255), nullable=False, unique=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('expires_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_verifications_id'), 'email_verifications', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop email_verifications table
    op.drop_index(op.f('ix_email_verifications_id'), table_name='email_verifications')
    op.drop_table('email_verifications')

    # Remove new columns from users table
    op.drop_column('users', 'availability')
    op.drop_column('users', 'social_links')
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'cover_photo')
    op.drop_column('users', 'phone')

    # Make gender and nationality non-nullable again
    op.alter_column('users', 'gender', existing_type=sa.String(), nullable=False)
    op.alter_column('users', 'nationality', existing_type=sa.String(), nullable=False)

    # Note: Cannot remove 'regular' enum value from PostgreSQL enum type directly
