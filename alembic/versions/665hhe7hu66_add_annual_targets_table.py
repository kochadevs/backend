"""add annual targets table

Revision ID: 665hhe7hu66
Revises: 554gge6gt55
Create Date: 2025-11-26 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '665hhe7hu66'
down_revision: Union[str, Sequence[str], None] = '554gge6gt55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    from sqlalchemy.dialects import postgresql

    # Create the enum type using Alembic's native support
    annual_target_status_enum = postgresql.ENUM(
        'not_started', 'in_progress', 'completed', 'overdue',
        name='annualtargetstatusenum',
        create_type=True
    )

    # Check if enum exists, create if it doesn't
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'annualtargetstatusenum')"
    ))
    if not result.scalar():
        annual_target_status_enum.create(conn, checkfirst=True)

    # Create annual_targets table
    op.create_table(
        'annual_targets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date_created', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_modified', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('objective', sa.Text(), nullable=False),
        sa.Column('measured_by', sa.String(), nullable=True),
        sa.Column('completed_by', sa.Date(), nullable=True),
        sa.Column('upload_path', sa.String(), nullable=True),
        sa.Column('status', postgresql.ENUM(
            'not_started', 'in_progress', 'completed', 'overdue',
            name='annualtargetstatusenum',
            create_type=False  # Don't create the type again
        ), nullable=False, server_default='not_started'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_annual_targets_id'), 'annual_targets', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    from sqlalchemy.dialects import postgresql

    # Drop annual_targets table
    op.drop_index(op.f('ix_annual_targets_id'), table_name='annual_targets')
    op.drop_table('annual_targets')

    # Drop enum type
    annual_target_status_enum = postgresql.ENUM(
        'not_started', 'in_progress', 'completed', 'overdue',
        name='annualtargetstatusenum'
    )
    annual_target_status_enum.drop(op.get_bind(), checkfirst=True)
