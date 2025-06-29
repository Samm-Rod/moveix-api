"""
add scheduled, freight_type, volume, round_trip to ride

Revision ID: 20250626_add_scheduled_freighttype_volume_roundtrip_to_ride
Revises: 20250626_altera_status_driverid_ride
Create Date: 2025-06-26

"""
from alembic import op
import sqlalchemy as sa

revision = '20250626_add_scheduled_freighttype_volume_roundtrip_to_ride'
down_revision = '20250626_altera_status_driverid_ride'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('rides', sa.Column('scheduled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('rides', sa.Column('freight_type', sa.String(), nullable=False, server_default='mudanca'))
    op.add_column('rides', sa.Column('volume', sa.Integer(), nullable=True))
    op.add_column('rides', sa.Column('round_trip', sa.Boolean(), nullable=False, server_default='false'))

def downgrade():
    op.drop_column('rides', 'scheduled')
    op.drop_column('rides', 'freight_type')
    op.drop_column('rides', 'volume')
    op.drop_column('rides', 'round_trip')
