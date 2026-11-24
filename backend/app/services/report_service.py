"""
CircuitDoctor - PDF Inspection Report Generator
Generates professional, publication-quality engineering inspection reports using ReportLab.
Includes visual evidence (original and annotated PCB images), defect breakdown tables,
and the mandatory optical inspection vs. electrical testing domain boundary disclaimer.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    KeepTogether,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from backend.app.models.inspection import Inspection
from backend.app.core.defect_classes import DEFECT_CLASSES, get_class_info

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "backend" / "reports"


class ReportService:

    @staticmethod
    def generate_inspection_report(inspection: Inspection) -> str:
        """
        Generate a professional PDF inspection report for the given Inspection database record.
        Returns the absolute filepath to the created PDF.
        """
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        pdf_filename = f"CircuitDoctor_Inspection_{inspection.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = REPORTS_DIR / pdf_filename

        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Custom typography styles
        brand_title_style = ParagraphStyle(
            "BrandTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
        )
        tagline_style = ParagraphStyle(
            "Tagline",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#0284c7"),
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#1e293b"),
            spaceBefore=10,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )
        table_cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1e293b"),
        )
        table_head_style = ParagraphStyle(
            "TableHead",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=colors.white,
        )
        disclaimer_heading = ParagraphStyle(
            "DisclaimerHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#b91c1c"),
        )
        disclaimer_body = ParagraphStyle(
            "DisclaimerBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10.5,
            textColor=colors.HexColor("#7f1d1d"),
            alignment=TA_JUSTIFY,
        )

        story = []

        # 1. Header with branding and inspection metadata
        header_data = [
            [
                Paragraph("<b>CIRCUITDOCTOR</b>", brand_title_style),
                Paragraph(f"<b>INSPECTION REPORT #{inspection.id:05d}</b>", ParagraphStyle(
                    "ReportNum",
                    parent=styles["Normal"],
                    fontName="Helvetica-Bold",
                    fontSize=12,
                    alignment=TA_RIGHT,
                    textColor=colors.HexColor("#0369a1")
                ))
            ],
            [
                Paragraph("Automated Optical PCB Defect Detection & Quality Analysis", tagline_style),
                Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", ParagraphStyle(
                    "Date",
                    parent=styles["Normal"],
                    fontName="Helvetica",
                    fontSize=8,
                    alignment=TA_RIGHT,
                    textColor=colors.HexColor("#64748b")
                ))
            ]
        ]
        header_table = Table(header_data, colWidths=[340, 200])
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=10))

        # 2. Executive KPI Summary Cards
        status_color = colors.HexColor("#16a34a") if inspection.inspection_status == "pass" else (
            colors.HexColor("#dc2626") if inspection.inspection_status == "fail" else colors.HexColor("#d97706")
        )
        status_text = inspection.inspection_status.upper()

        summary_box_data = [
            [
                Paragraph("<b>Inspection Status</b>", table_cell_style),
                Paragraph("<b>Total Defects Detected</b>", table_cell_style),
                Paragraph("<b>Inference Latency</b>", table_cell_style),
                Paragraph("<b>Model Architecture</b>", table_cell_style),
            ],
            [
                Paragraph(f"<font color='{status_color.hexval()}'><b>{status_text}</b></font>", ParagraphStyle("StatusVal", fontName="Helvetica-Bold", fontSize=14, leading=16)),
                Paragraph(f"<b>{inspection.total_defects}</b>", ParagraphStyle("DefectVal", fontName="Helvetica-Bold", fontSize=14, leading=16, textColor=colors.HexColor("#0f172a"))),
                Paragraph(f"<b>{inspection.inference_time:.1f} ms</b>", ParagraphStyle("TimeVal", fontName="Helvetica", fontSize=12, leading=14, textColor=colors.HexColor("#334155"))),
                Paragraph(f"{inspection.model_version}", ParagraphStyle("ModelVal", fontName="Helvetica", fontSize=10, leading=12, textColor=colors.HexColor("#0284c7"))),
            ],
            [
                Paragraph(f"<b>Source Image:</b> {Path(inspection.original_filename).name}", body_style),
                Paragraph(f"<b>Resolution:</b> {inspection.image_width or 'N/A'} x {inspection.image_height or 'N/A'} px", body_style),
                Paragraph(f"<b>Confidence Threshold:</b> {inspection.confidence_threshold:.2f}", body_style),
                Paragraph(f"<b>Standard:</b> DeepPCB / IPC-A-600", body_style),
            ]
        ]
        summary_table = Table(summary_box_data, colWidths=[135, 135, 135, 135])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("SPAN", (0, 2), (1, 2)),
            ("SPAN", (2, 2), (3, 2)),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 12))

        # 3. Visual Evidence Section (Side-by-side or stacked images)
        story.append(Paragraph("<b>VISUAL INSPECTION EVIDENCE</b>", section_heading))

        orig_path = Path(inspection.stored_image_path) if inspection.stored_image_path else None
        annot_path = Path(inspection.annotated_image_path) if inspection.annotated_image_path else None

        img_cells = []
        if orig_path and orig_path.exists():
            img_cells.append([
                Paragraph("<b>Original PCB Under Inspection</b>", table_cell_style),
                RLImage(str(orig_path), width=3.3 * inch, height=3.3 * inch)
            ])
        else:
            img_cells.append([
                Paragraph("<b>Original PCB</b>", table_cell_style),
                Paragraph("Original image file not available", body_style)
            ])

        if annot_path and annot_path.exists():
            img_cells.append([
                Paragraph("<b>AI Defect Localization Overlay</b>", table_cell_style),
                RLImage(str(annot_path), width=3.3 * inch, height=3.3 * inch)
            ])
        else:
            img_cells.append([
                Paragraph("<b>AI Defect Overlay</b>", table_cell_style),
                Paragraph("Annotated image file not available", body_style)
            ])

        evidence_table = Table([
            [img_cells[0][0], img_cells[1][0]],
            [img_cells[0][1], img_cells[1][1]],
        ], colWidths=[265, 265])
        evidence_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(evidence_table)
        story.append(Spacer(1, 12))

        # 4. Detected Defects Detail Table
        story.append(Paragraph("<b>DEFECT FINDINGS & LOCALIZATION TABLE</b>", section_heading))

        if not inspection.detections:
            story.append(Paragraph("No surface anomalies detected. PCB passed optical defect inspection.", body_style))
        else:
            defect_table_rows = [
                [
                    Paragraph("<b>#</b>", table_head_style),
                    Paragraph("<b>Class Name</b>", table_head_style),
                    Paragraph("<b>Severity</b>", table_head_style),
                    Paragraph("<b>Conf</b>", table_head_style),
                    Paragraph("<b>Bounding Box (x1, y1, x2, y2)</b>", table_head_style),
                    Paragraph("<b>Recommended Electrical Action</b>", table_head_style),
                ]
            ]

            for idx, det in enumerate(inspection.detections):
                class_info = get_class_info(det.class_id)
                sev = class_info.get("severity", "medium").upper()
                advice = class_info.get("verification_advice", "Electrical testing required.")
                sev_color = "#dc2626" if sev == "CRITICAL" else ("#d97706" if sev == "MEDIUM" else "#0284c7")

                defect_table_rows.append([
                    Paragraph(str(idx + 1), table_cell_style),
                    Paragraph(f"<b>{det.class_name}</b>", table_cell_style),
                    Paragraph(f"<font color='{sev_color}'><b>{sev}</b></font>", table_cell_style),
                    Paragraph(f"{det.confidence * 100:.1f}%", table_cell_style),
                    Paragraph(f"[{det.x1}, {det.y1}, {det.x2}, {det.y2}]", table_cell_style),
                    Paragraph(advice, table_cell_style),
                ])

            defect_table = Table(
                defect_table_rows,
                colWidths=[24, 90, 56, 45, 125, 200]
            )
            defect_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(defect_table)

        story.append(Spacer(1, 14))

        # 5. Mandatory Engineering Disclaimer & Electrical Boundary Notice
        disclaimer_box = [
            [
                Paragraph("<b>CRITICAL ENGINEERING LIMITATION: OPTICAL INSPECTION VS. ELECTRICAL TESTING</b>", disclaimer_heading)
            ],
            [
                Paragraph(
                    "<b>Notice of Inspection Scope:</b> The detections highlighted in this report represent visual anomaly predictions "
                    "derived from 2D optical surface imaging and an Ultralytics YOLO deep learning object detector. Optical inspection "
                    "identifies geometric surface pattern discrepancies (e.g. spurious copper, trace necking, missing drill holes) "
                    "against training baselines. However, <b>optical inspection cannot conclusively diagnose electrical functionality</b>.<br/><br/>"
                    "• <b>Open Circuit Verification:</b> Apparent copper discontinuities must be verified using flying-probe or bed-of-nails "
                    "continuity testing to rule out subsurface layer connections.<br/>"
                    "• <b>Short Circuit Verification:</b> Apparent trace bridges must undergo high-voltage isolation / hi-pot testing to confirm "
                    "true galvanic conduction versus inert surface particulates.<br/>"
                    "• <b>Mouse Bites & Spurs:</b> Trace necking and spurs require 4-wire Kelvin micro-ohm resistance measurements and IPC-2221 "
                    "clearance verification to validate signal integrity and dielectric breakdown safety.",
                    disclaimer_body
                )
            ]
        ]
        disclaimer_table = Table(disclaimer_box, colWidths=[540])
        disclaimer_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fef2f2")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#f87171")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(KeepTogether(disclaimer_table))

        # Build document
        doc.build(story)
        print(f"[ReportService] Generated PDF report: {pdf_path}")
        return str(pdf_path.resolve())
