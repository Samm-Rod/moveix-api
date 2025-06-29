"""
Altera status inicial e driver_id para nullable em rides

Revision ID: 20250626_altera_status_driverid_ride
Revises: 20250625_add_2fa_and_reset_fields_to_driver
Create Date: 2025-06-26

"""
from alembic import op
import sqlalchemy as sa

revision = '20250626_altera_status_driverid_ride'
down_revision = '20250625_add_2fa_and_reset_fields_to_driver'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('rides', 'driver_id', existing_type=sa.Integer(), nullable=True)
    op.alter_column('rides', 'status', existing_type=sa.String(), server_default='disponivel')

def downgrade():
    op.alter_column('rides', 'driver_id', existing_type=sa.Integer(), nullable=False)
    op.alter_column('rides', 'status', existing_type=sa.String(), server_default='pending')
