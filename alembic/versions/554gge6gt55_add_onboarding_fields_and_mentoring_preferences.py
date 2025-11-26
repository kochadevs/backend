"""add onboarding fields and mentoring preferences

Revision ID: 554gge6gt55
Revises: 453ff45fs44
Create Date: 2025-11-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '554gge6gt55'
down_revision: Union[str, Sequence[str], None] = '453ff45fs44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns to users table for onboarding
    op.add_column('users', sa.Column('company', sa.String(), nullable=True))
    op.add_column('users', sa.Column('years_of_experience', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('long_term_goals', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('code_of_conduct_accepted', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('onboarding_completed', sa.Boolean(), nullable=False, server_default='false'))

    # Create mentoring_frequency table
    op.create_table(
        'mentoring_frequency',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date_created', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_modified', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mentoring_frequency_id'), 'mentoring_frequency', ['id'], unique=False)

    # Create mentoring_format table
    op.create_table(
        'mentoring_format',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date_created', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_modified', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mentoring_format_id'), 'mentoring_format', ['id'], unique=False)

    # Create user_mentoring_frequency_assosciation table
    op.create_table(
        'user_mentoring_frequency_assosciation',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('mentoring_frequency_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['mentoring_frequency_id'], ['mentoring_frequency.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'mentoring_frequency_id')
    )

    # Create user_mentoring_format_assosciation table
    op.create_table(
        'user_mentoring_format_assosciation',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('mentoring_format_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['mentoring_format_id'], ['mentoring_format.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'mentoring_format_id')
    )

    # Insert default mentoring frequency options
    op.execute("""
        INSERT INTO mentoring_frequency (name) VALUES
        ('Weekly'),
        ('Bi-weekly'),
        ('Monthly')
        ON CONFLICT (name) DO NOTHING;
    """)

    # Insert default mentoring format options
    op.execute("""
        INSERT INTO mentoring_format (name) VALUES
        ('Video Call'),
        ('Phone Call'),
        ('Chat'),
        ('In-Person')
        ON CONFLICT (name) DO NOTHING;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop association tables
    op.drop_table('user_mentoring_format_assosciation')
    op.drop_table('user_mentoring_frequency_assosciation')

    # Drop mentoring tables
    op.drop_index(op.f('ix_mentoring_format_id'), table_name='mentoring_format')
    op.drop_table('mentoring_format')
    op.drop_index(op.f('ix_mentoring_frequency_id'), table_name='mentoring_frequency')
    op.drop_table('mentoring_frequency')

    # Remove columns from users table
    op.drop_column('users', 'onboarding_completed')
    op.drop_column('users', 'code_of_conduct_accepted')
    op.drop_column('users', 'long_term_goals')
    op.drop_column('users', 'years_of_experience')
    op.drop_column('users', 'company')
