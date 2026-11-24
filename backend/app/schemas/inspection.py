"""
CircuitDoctor - Pydantic Request & Response Schemas
Type-safe validation for all API inputs and outputs using Pydantic v2.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# --- Detection Schemas ---

class DetectionBase(BaseModel):
    class_id: int = Field(..., ge=0, le=10, description="Defect class identifier")
    class_name: str = Field(..., description="Human-readable defect class name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model prediction confidence score")
    x1: float = Field(..., description="Bounding box top-left X coordinate")
    y1: float = Field(..., description="Bounding box top-left Y coordinate")
    x2: float = Field(..., description="Bounding box bottom-right X coordinate")
    y2: float = Field(..., description="Bounding box bottom-right Y coordinate")

class DetectionCreate(DetectionBase):
    pass

class DetectionResponse(DetectionBase):
    id: int
    inspection_id: int
    model_config = ConfigDict(from_attributes=True)


# --- Inspection Schemas ---

class InspectionBase(BaseModel):
    original_filename: str
    total_defects: int
    inspection_status: str
    model_version: str
    confidence_threshold: float
    inference_time: float
    image_width: Optional[int] = None
    image_height: Optional[int] = None

class InspectionCreate(InspectionBase):
    stored_image_path: str
    annotated_image_path: Optional[str] = None
    detections: List[DetectionCreate] = []

class InspectionResponse(InspectionBase):
    id: int
    stored_image_path: str
    annotated_image_path: Optional[str] = None
    created_at: datetime
    detections: List[DetectionResponse] = []
    
    # URL paths for frontend consumption
    original_image_url: Optional[str] = None
    annotated_image_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class InspectionSummary(BaseModel):
    id: int
    original_filename: str
    total_defects: int
    inspection_status: str
    model_version: str
    confidence_threshold: float
    inference_time: float
    created_at: datetime
    defect_counts: Dict[str, int] = {}
    original_image_url: Optional[str] = None
    annotated_image_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# --- Health & Metadata Schemas ---

class HealthResponse(BaseModel):
    status: str = Field("healthy", description="Overall backend health status")
    project: str = Field("CircuitDoctor", description="Application name")
    version: str = Field("1.0.0", description="API version")
    model_status: str = Field(..., description="AI Model availability: 'ready', 'not_found', 'error'")
    model_path: str
    device: str = Field("cpu", description="Compute device: 'cuda' or 'cpu'")
    database_status: str = Field("connected", description="SQLite database connectivity")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ClassInfo(BaseModel):
    id: int
    name: str
    key: str
    description: str
    color_hex: str
    severity: str
    electrical_risk: str
    verification_advice: str

class ModelInfoResponse(BaseModel):
    model_name: str
    model_architecture: str
    model_version: str
    model_status: str
    model_path: str
    weights_exist: bool
    weights_size_bytes: Optional[int] = None
    device: str
    cuda_available: bool
    gpu_name: Optional[str] = None
    total_gpu_memory_mb: Optional[int] = None
    supported_classes: List[ClassInfo]
    default_confidence_threshold: float
    default_iou_threshold: float
    training_metrics: Optional[Dict[str, Any]] = None


# --- Statistics Schemas ---

class DefectDistributionItem(BaseModel):
    class_id: int
    class_name: str
    count: int
    percentage: float
    color_hex: str
    severity: str

class StatisticsResponse(BaseModel):
    total_inspections: int
    total_defects_detected: int
    total_images_inspected: int
    defect_free_inspections: int
    defective_inspections: int
    average_inference_time_ms: float
    defect_distribution: List[DefectDistributionItem]
    recent_inspections_count: int
    model_status: str
