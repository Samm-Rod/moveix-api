"""add rating to ride

Revision ID: 20240624_rating
Revises: df09ff112e3e
Create Date: 2024-06-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240624_rating'
down_revision = 'df09ff112e3e'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('rides', sa.Column('rating', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('rides', 'rating')
