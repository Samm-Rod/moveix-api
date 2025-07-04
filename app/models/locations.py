from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey('rides.id'), nullable=False)
    latitude = Column(String, nullable=False)
    longitude = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    
    ride = relationship("Ride", back_populates="locations")

    def __repr__(self):
        return f"<Location(ride_id={self.ride_id}, latitude={self.latitude}, longitude={self.longitude})>"