from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e8a60a1902fd'
down_revision: Union[str, Sequence[str], None] = 'a6d24b61d02e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Declarar os ENUMs
from sqlalchemy.dialects import postgresql

# Adicione isso antes de usar os Enums nas colunas
vehicle_status_enum = postgresql.ENUM('ACTIVE', 'INACTIVE', 'UNDER_REVIEW', name='vehicle_status')
license_category_enum = postgresql.ENUM('A', 'B', 'C', 'D', 'E', 'AB', name='license_category')
vehicle_size_enum = postgresql.ENUM('SMALL', 'MEDIUM', 'LARGE', name='vehicle_size')


def upgrade():
    vehicle_status_enum = sa.Enum('ACTIVE', 'INACTIVE', 'UNDER_REVIEW', name='vehicle_status')
    license_category_enum = sa.Enum('A', 'B', 'C', 'D', 'E', 'AB', name='license_category')
    vehicle_size_enum = sa.Enum('SMALL', 'MEDIUM', 'LARGE', name='vehicle_size')

    # Cria os tipos ENUM no banco
    vehicle_status_enum.create(op.get_bind(), checkfirst=True)
    license_category_enum.create(op.get_bind(), checkfirst=True)
    vehicle_size_enum.create(op.get_bind(), checkfirst=True)

    op.drop_column('vehicles', 'active')

    op.add_column('vehicles', sa.Column('status', vehicle_status_enum, nullable=True))

    op.alter_column('vehicles', 'license_category',
        existing_type=sa.VARCHAR(),
        type_=license_category_enum,
        nullable=False
    )

    op.alter_column('vehicles', 'size',
        existing_type=sa.VARCHAR(),
        type_=vehicle_size_enum,
        existing_nullable=False,
        existing_server_default=sa.text("'P'::character varying")
    )



def downgrade() -> None:
    # Volta à versão anterior
    op.add_column('vehicles', sa.Column('active', sa.BOOLEAN(), nullable=True))
    op.alter_column('vehicles', 'size',
               existing_type=sa.Enum('SMALL', 'MEDIUM', 'LARGE', name='vehicle_size'),
               type_=sa.VARCHAR(),
               existing_nullable=False,
               existing_server_default=sa.text("'P'::character varying"))
    op.alter_column('vehicles', 'license_category',
               existing_type=sa.Enum('A', 'B', 'C', 'D', 'E', 'AB', name='license_category'),
               type_=sa.VARCHAR(),
               nullable=True)
    op.drop_column('vehicles', 'status')

    # Drop dos tipos ENUM
    vehicle_status_enum = sa.Enum('ACTIVE', 'INACTIVE', 'UNDER_REVIEW', name='vehicle_status')
    vehicle_status_enum.drop(op.get_bind(), checkfirst=True)

    license_category_enum = sa.Enum('A', 'B', 'C', 'D', 'E', 'AB', name='license_category')
    license_category_enum.drop(op.get_bind(), checkfirst=True)

    vehicle_size_enum = sa.Enum('SMALL', 'MEDIUM', 'LARGE', name='vehicle_size')
    vehicle_size_enum.drop(op.get_bind(), checkfirst=True)


