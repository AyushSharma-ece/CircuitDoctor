"""
CircuitDoctor - Annotation Coordinate & Class Mapping Converter
Converts raw DeepPCB format (x1, y1, x2, y2, raw_type) into standard YOLO format
(class_id, x_center, y_center, width, height) with strict boundary validation.
"""

from typing import List, Tuple, Dict, Any, Optional

# DeepPCB raw class ID (1-6) -> CircuitDoctor standard YOLO class ID (0-5)
DEEPPCB_RAW_TO_YOLO: Dict[int, int] = {
    6: 0,  # pin-hole -> Missing Hole
    3: 1,  # mousebite -> Mouse Bite
    1: 2,  # open -> Open Circuit
    2: 3,  # short -> Short
    4: 4,  # spur -> Spur
    5: 5,  # copper -> Spurious Copper
}

RAW_TYPE_NAMES = {
    1: "open",
    2: "short",
    3: "mousebite",
    4: "spur",
    5: "copper",
    6: "pin-hole"
}

def convert_box_to_yolo(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    img_w: int = 640,
    img_h: int = 640
) -> Tuple[float, float, float, float]:
    """
    Convert absolute pixel coordinates (x1, y1, x2, y2) to normalized
    YOLO center coordinates and dimensions (cx, cy, w, h).
    """
    # Fix inverted coordinates if present
    x_min = min(x1, x2)
    x_max = max(x1, x2)
    y_min = min(y1, y2)
    y_max = max(y1, y2)

    # Clamp to image boundaries
    x_min = max(0.0, min(float(x_min), float(img_w)))
    x_max = max(0.0, min(float(x_max), float(img_w)))
    y_min = max(0.0, min(float(y_min), float(img_h)))
    y_max = max(0.0, min(float(y_max), float(img_h)))

    box_w = x_max - x_min
    box_h = y_max - y_min

    # Prevent division by zero or degenerate boxes
    if box_w <= 0 or box_h <= 0 or img_w <= 0 or img_h <= 0:
        return (0.0, 0.0, 0.0, 0.0)

    center_x = (x_min + x_max) / 2.0 / float(img_w)
    center_y = (y_min + y_max) / 2.0 / float(img_h)
    norm_w = box_w / float(img_w)
    norm_h = box_h / float(img_h)

    # Clamp normalized coordinates strictly within [0.0, 1.0]
    center_x = max(0.0, min(1.0, center_x))
    center_y = max(0.0, min(1.0, center_y))
    norm_w = max(0.0, min(1.0, norm_w))
    norm_h = max(0.0, min(1.0, norm_h))

    return (
        round(center_x, 6),
        round(center_y, 6),
        round(norm_w, 6),
        round(norm_h, 6)
    )

def parse_deeppcb_annotation_line(
    line: str,
    img_w: int = 640,
    img_h: int = 640
) -> Optional[Tuple[int, float, float, float, float]]:
    """
    Parse a single line from a DeepPCB annotation file:
    Format: x1 y1 x2 y2 type
    Returns: (yolo_class_id, center_x, center_y, width, height) or None if invalid.
    """
    parts = line.strip().split()
    if len(parts) < 5:
        # Some annotations might be comma-separated
        parts = line.strip().replace(',', ' ').split()
        if len(parts) < 5:
            return None

    try:
        x1 = float(parts[0])
        y1 = float(parts[1])
        x2 = float(parts[2])
        y2 = float(parts[3])
        raw_type = int(parts[4])
    except (ValueError, IndexError):
        return None

    if raw_type not in DEEPPCB_RAW_TO_YOLO:
        return None

    yolo_class_id = DEEPPCB_RAW_TO_YOLO[raw_type]
    cx, cy, w, h = convert_box_to_yolo(x1, y1, x2, y2, img_w, img_h)

    # Discard non-positive dimensions
    if w <= 0.001 or h <= 0.001:
        return None

    return (yolo_class_id, cx, cy, w, h)

def parse_deeppcb_annotation_file(
    file_path: str,
    img_w: int = 640,
    img_h: int = 640
) -> List[Tuple[int, float, float, float, float]]:
    """Parse complete DeepPCB annotation text file into list of YOLO bbox tuples."""
    results = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parsed = parse_deeppcb_annotation_line(line, img_w, img_h)
            if parsed is not None:
                results.append(parsed)
    return results

def format_yolo_lines(boxes: List[Tuple[int, float, float, float, float]]) -> str:
    """Format list of YOLO boxes as standard YOLO annotation string."""
    return "\n".join(f"{cid} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}" for cid, cx, cy, w, h in boxes)
