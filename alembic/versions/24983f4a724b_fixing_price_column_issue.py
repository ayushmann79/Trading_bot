from alembic import op
import sqlalchemy as sa
import sqlalchemy.engine.reflection as alembic_reflection


# Revision identifiers, used by Alembic.
revision = '24983f4a724b'  # Keep your latest revision ID
down_revision = 'a66d5a6b606e'  # Keep your previous migration ID
branch_labels = None
depends_on = None


def upgrade():
    # ✅ Step 1: Get the current table columns
    conn = op.get_bind()
    inspector = alembic_reflection.Inspector.from_engine(conn)
    columns = [col["name"] for col in inspector.get_columns("trades")]

    # ✅ Step 2: Add new columns ONLY if they don't exist
    if "token" not in columns:
        op.add_column('trades', sa.Column('token', sa.String(), nullable=True))

    if "price" not in columns:
        op.add_column('trades', sa.Column('price', sa.Float(), nullable=True))

    # ✅ Step 3: Fill existing NULL values with default values
    if "token" in columns:
        op.execute("UPDATE trades SET token = 'unknown' WHERE token IS NULL")

    if "price" in columns:
        op.execute("UPDATE trades SET price = 0.0 WHERE price IS NULL")

    # ✅ Step 4: Change columns to NOT NULL after filling existing data
    if "token" in columns:
        op.alter_column('trades', 'token', nullable=False)

    if "price" in columns:
        op.alter_column('trades', 'price', nullable=False)


def downgrade():
    # ✅ Rollback changes by dropping new columns (if they exist)
    conn = op.get_bind()
    inspector = alembic_reflection.Inspector.from_engine(conn)
    columns = [col["name"] for col in inspector.get_columns("trades")]

    if "token" in columns:
        op.drop_column('trades', 'token')

    if "price" in columns:
        op.drop_column('trades', 'price')
