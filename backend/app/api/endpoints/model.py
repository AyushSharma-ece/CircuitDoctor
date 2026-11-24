"""
CircuitDoctor - Model Information Endpoint
GET /api/model/info
Returns real model configuration, GPU telemetry, supported defect classes, and evaluation metrics.
"""

import json
from pathlib import Path
from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.core.defect_classes import get_all_classes
from backend.app.schemas.inspection import ModelInfoResponse, ClassInfo
from backend.app.api.endpoints.health import check_model_status

router = APIRouter()

EVAL_METRICS_PATH = settings.MODELS_DIR / "evaluation_metrics.json"
TRAIN_SUMMARY_PATH = settings.MODELS_DIR / "training_summary.json"


@router.get("/model/info", response_model=ModelInfoResponse)
def get_model_info():
    """Returns actual AI model configuration, architecture details, and hardware status."""
    cuda_avail = False
    gpu_name = None
    vram_mb = None
    device = "cpu"

    try:
        import torch
        cuda_avail = torch.cuda.is_available()
        if cuda_avail:
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            vram_mb = int(torch.cuda.get_device_properties(0).total_memory / (1024 * 1024))
    except Exception:
        pass

    weights_exist = settings.MODEL_PATH.exists()
    weights_size = settings.MODEL_PATH.stat().st_size if weights_exist else None
    model_status = check_model_status()

    classes_data = [ClassInfo(**c) for c in get_all_classes()]

    # Load evaluation metrics if available
    training_metrics = None
    if EVAL_METRICS_PATH.exists():
        try:
            with open(EVAL_METRICS_PATH, "r") as f:
                training_metrics = json.load(f)
        except Exception:
            pass
    elif TRAIN_SUMMARY_PATH.exists():
        try:
            with open(TRAIN_SUMMARY_PATH, "r") as f:
                training_metrics = json.load(f)
        except Exception:
            pass

    return ModelInfoResponse(
        model_name=settings.MODEL_NAME,
        model_architecture=settings.MODEL_ARCHITECTURE,
        model_version=f"{settings.MODEL_ARCHITECTURE}-v1.0",
        model_status=model_status,
        model_path=str(settings.MODEL_PATH),
        weights_exist=weights_exist,
        weights_size_bytes=weights_size,
        device=device,
        cuda_available=cuda_avail,
        gpu_name=gpu_name,
        total_gpu_memory_mb=vram_mb,
        supported_classes=classes_data,
        default_confidence_threshold=settings.DEFAULT_CONFIDENCE_THRESHOLD,
        default_iou_threshold=settings.DEFAULT_IOU_THRESHOLD,
        training_metrics=training_metrics
    )
