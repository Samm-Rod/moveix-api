"""
add 2fa and reset fields to client

Revision ID: 20250625_add_2fa_and_reset_fields_to_client
Revises: 20240624_rating
Create Date: 2025-06-25

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250625_add_2fa_and_reset_fields_to_client'
down_revision = '20240624_rating'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('clients', sa.Column('two_fa_secret', sa.String(), nullable=True))
    op.add_column('clients', sa.Column('reset_code', sa.String(), nullable=True))

def downgrade():
    op.drop_column('clients', 'two_fa_secret')
    op.drop_column('clients', 'reset_code')
