"""
CircuitDoctor - Core Defect Categories Configuration
Single Source of Truth for PCB Defect Classification.

DeepPCB Standard Mapping (Tang et al., 2019):
  0 - Missing Hole
  1 - Mouse Bite
  2 - Open Circuit
  3 - Short
  4 - Spur
  5 - Spurious Copper
"""

from typing import Dict, Any, List

DEFECT_CLASSES: Dict[int, Dict[str, Any]] = {
    0: {
        "id": 0,
        "name": "Missing Hole",
        "key": "missing_hole",
        "description": "Via or through-hole missing from required drill location on the PCB surface.",
        "color_hex": "#ef4444",      # Red
        "color_rgb": (239, 68, 68),
        "severity": "critical",
        "electrical_risk": "Break in layer-to-layer interconnect or missing component pin mount.",
        "verification_advice": "Perform continuity check and optical coordinate measurement to verify drill hole existence."
    },
    1: {
        "id": 1,
        "name": "Mouse Bite",
        "key": "mouse_bite",
        "description": "Erosion or nick along trace edges or board boundaries causing local necking.",
        "color_hex": "#f97316",      # Orange
        "color_rgb": (249, 115, 22),
        "severity": "medium",
        "electrical_risk": "Reduced cross-sectional area leading to increased trace resistance and localized heating.",
        "verification_advice": "Perform 4-wire milliohm resistance check across suspect trace section."
    },
    2: {
        "id": 2,
        "name": "Open Circuit",
        "key": "open_circuit",
        "description": "Unintended complete break or discontinuity in a conductive copper trace.",
        "color_hex": "#dc2626",      # Bright Red
        "color_rgb": (220, 38, 38),
        "severity": "critical",
        "electrical_risk": "Total loss of signal propagation or power delivery along the affected net.",
        "verification_advice": "Perform digital multimeter continuity / flying-probe electrical test."
    },
    3: {
        "id": 3,
        "name": "Short",
        "key": "short",
        "description": "Unintended copper bridging or connection between two electrically distinct nets.",
        "color_hex": "#b91c1c",      # Dark Red
        "color_rgb": (185, 28, 28),
        "severity": "critical",
        "electrical_risk": "Overcurrent damage, ground fault, or logic malfunction.",
        "verification_advice": "Perform isolation resistance / high-pot testing between adjacent nets."
    },
    4: {
        "id": 4,
        "name": "Spur",
        "key": "spur",
        "description": "Pointed copper protrusion projecting outwards from a conductor trace.",
        "color_hex": "#eab308",      # Yellow
        "color_rgb": (234, 179, 8),
        "severity": "medium",
        "electrical_risk": "Reduced clearance distance to adjacent nets; risk of dielectric breakdown.",
        "verification_advice": "Check minimum trace clearance spacing against IPC-2221 design rules."
    },
    5: {
        "id": 5,
        "name": "Spurious Copper",
        "key": "spurious_copper",
        "description": "Isolated residual copper island or speck left behind after chemical etching.",
        "color_hex": "#38bdf8",      # Sky Blue
        "color_rgb": (56, 189, 248),
        "severity": "low",
        "electrical_risk": "Potential parasitic capacitance or debris migration under vibration.",
        "verification_advice": "Verify galvanic isolation from all adjacent functional nets."
    }
}

CLASS_ID_TO_NAME: Dict[int, str] = {
    class_id: info["name"] for class_id, info in DEFECT_CLASSES.items()
}

CLASS_NAME_TO_ID: Dict[str, int] = {
    info["name"].lower(): class_id for class_id, info in DEFECT_CLASSES.items()
}

def get_class_name(class_id: int) -> str:
    """Return standard defect class name for given class id."""
    return CLASS_ID_TO_NAME.get(class_id, f"Unknown Defect ({class_id})")

def get_class_info(class_id: int) -> Dict[str, Any]:
    """Return comprehensive metadata dictionary for a defect class."""
    return DEFECT_CLASSES.get(class_id, {
        "id": class_id,
        "name": f"Unknown ({class_id})",
        "key": f"unknown_{class_id}",
        "description": "Unregistered defect class.",
        "color_hex": "#94a3b8",
        "color_rgb": (148, 163, 184),
        "severity": "low",
        "electrical_risk": "Unspecified.",
        "verification_advice": "Manual visual and electrical verification required."
    })

def get_all_classes() -> List[Dict[str, Any]]:
    """Return ordered list of all registered defect class definitions."""
    return [DEFECT_CLASSES[cid] for cid in sorted(DEFECT_CLASSES.keys())]
