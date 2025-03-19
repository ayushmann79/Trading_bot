"""Add timestamp column to trades

Revision ID: 7b9b2b08fd77
Revises: 24983f4a724b
Create Date: 2025-03-14 18:27:10.304779

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision: str = '7b9b2b08fd77'
down_revision: Union[str, None] = '24983f4a724b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ✅ Step 1: Add timestamp column with NULL allowed temporarily
    op.add_column('trades', sa.Column('timestamp', sa.DateTime(), nullable=True))

    # ✅ Step 2: Fill existing NULL timestamps with current timestamp
    op.execute("UPDATE trades SET timestamp = NOW() WHERE timestamp IS NULL")

    # ✅ Step 3: Set timestamp column to NOT NULL
    op.alter_column('trades', 'timestamp', nullable=False)

    # ✅ Step 4: Ensure all NULL values in price are updated before setting NOT NULL
    op.execute("UPDATE trades SET price = 0.0 WHERE price IS NULL")

    # ✅ Step 5: Alter columns to required types
    op.alter_column('trades', 'amount',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=False)

    op.alter_column('trades', 'price',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)


def downgrade() -> None:
    # ✅ Rollback changes
    op.alter_column('trades', 'price',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)

    op.alter_column('trades', 'amount',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=False)

    op.drop_column('trades', 'timestamp')
