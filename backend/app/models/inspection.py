"""
CircuitDoctor - SQLAlchemy Database Models
Defines Inspections and Detections with foreign key cascades.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_image_path = Column(String(500), nullable=False)
    annotated_image_path = Column(String(500), nullable=True)
    total_defects = Column(Integer, default=0, nullable=False)
    inspection_status = Column(String(50), default="completed", nullable=False) # "completed", "no_defects", "failed"
    model_version = Column(String(50), default="YOLO26n-v1.0", nullable=False)
    confidence_threshold = Column(Float, default=0.25, nullable=False)
    inference_time = Column(Float, default=0.0, nullable=False) # In seconds
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Cascading one-to-many relationship with detections
    detections = relationship("Detection", back_populates="inspection", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Inspection id={self.id} file={self.original_filename} defects={self.total_defects}>"


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(Integer, nullable=False)
    class_name = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    x1 = Column(Float, nullable=False)
    y1 = Column(Float, nullable=False)
    x2 = Column(Float, nullable=False)
    y2 = Column(Float, nullable=False)

    inspection = relationship("Inspection", back_populates="detections")

    def __repr__(self):
        return f"<Detection id={self.id} class='{self.class_name}' conf={self.confidence:.2f}>"
