from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class RedNotice(Base):
    """Red Notice model for database"""
    __tablename__ = 'red_notices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    age = Column(String(50), nullable=True)
    nationality = Column(String(100), nullable=True)
    image_url = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<RedNotice(id={self.id}, name='{self.name}', nationality='{self.nationality}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'nationality': self.nationality,
            'image_url': self.image_url,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at is not None else None,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        } 