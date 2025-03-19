from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = 'a66d5a6b606e'  # Keep your latest revision ID
down_revision = '1ce0a31fd346'  # Keep your previous migration ID
branch_labels = None
depends_on = None


def upgrade():
    # ✅ Step 1: Add new columns (allow NULL temporarily to avoid errors)
    op.add_column('trades', sa.Column('token', sa.String(), nullable=True))  # Adding token column
    op.add_column('trades', sa.Column('price', sa.Float(), nullable=True))   # Adding price column

    # ✅ Step 2: Fill existing rows with default values
    op.execute("UPDATE trades SET token = 'unknown' WHERE token IS NULL")
    op.execute("UPDATE trades SET price = 0.0 WHERE price IS NULL")

    # ✅ Step 3: Set columns to NOT NULL after filling existing data
    op.alter_column('trades', 'token', nullable=False)
    op.alter_column('trades', 'price', nullable=False)


def downgrade():
    # ✅ Rollback changes by dropping new columns
    op.drop_column('trades', 'token')
    op.drop_column('trades', 'price')
