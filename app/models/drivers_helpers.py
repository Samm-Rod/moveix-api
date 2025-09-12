from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.database import Base

drivers_helpers = Table(
    'drivers_helpers',
    Base.metadata, 
    Column('driver_id', Integer, ForeignKey('drivers.id'), primary_key=True),
    Column('helper_id', Integer, ForeignKey('helpers.id'), primary_key=True)
)