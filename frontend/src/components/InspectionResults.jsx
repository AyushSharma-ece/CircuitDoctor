import React, { useState } from 'react';
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  Download,
  Eye,
  RefreshCw,
  Layers,
  Cpu,
  Clock,
  ShieldAlert,
  Sliders,
  ExternalLink
} from 'lucide-react';
import { getReportDownloadUrl, getOriginalImageUrl, getAnnotatedImageUrl } from '../services/api';

export default function InspectionResults({ inspection, onReset }) {
  const [viewMode, setViewMode] = useState('annotated'); // 'annotated', 'original', 'split'

  if (!inspection) return null;

  const totalDefects = inspection.total_defects || 0;
  const isPass = inspection.inspection_status === 'pass';
  const isFail = inspection.inspection_status === 'fail';
  const isWarning = inspection.inspection_status === 'warning';

  const statusColor = isPass
    ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
    : isFail
    ? 'text-rose-400 bg-rose-500/10 border-rose-500/30'
    : 'text-amber-400 bg-amber-500/10 border-amber-500/30';

  const statusIcon = isPass ? (
    <CheckCircle className="w-5 h-5 text-emerald-400" />
  ) : isFail ? (
    <XCircle className="w-5 h-5 text-rose-400" />
  ) : (
    <AlertTriangle className="w-5 h-5 text-amber-400" />
  );

  const originalUrl = inspection.original_image_url || getOriginalImageUrl(inspection.id);
  const annotatedUrl = inspection.annotated_image_url || getAnnotatedImageUrl(inspection.id);
  const reportUrl = inspection.report_url || getReportDownloadUrl(inspection.id);

  // Group detections by class for quick breakdown
  const categoryCounts = {};
  (inspection.detections || []).forEach((d) => {
    categoryCounts[d.class_name] = (categoryCounts[d.class_name] || 0) + 1;
  });

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Action & Status Bar */}
      <div className="card-industrial p-5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-navy-950 border border-charcoal-700">
            {statusIcon}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white tracking-wide">
                Inspection Report #{String(inspection.id).padStart(5, '0')}
              </h2>
              <span className={`px-2.5 py-0.5 rounded text-xs font-bold uppercase tracking-wider border ${statusColor}`}>
                {inspection.inspection_status}
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono mt-0.5">
              {inspection.original_filename} • {new Date(inspection.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onReset}
            className="px-3.5 py-2 bg-charcoal-800 hover:bg-charcoal-700 text-slate-200 text-xs font-semibold rounded-lg border border-charcoal-600 transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>New Inspection</span>
          </button>
          <a
            href={reportUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 bg-circuit-blue hover:bg-circuit-blue/90 text-navy-950 text-xs font-bold rounded-lg transition-all flex items-center gap-1.5 shadow-md"
          >
            <Download className="w-4 h-4" />
            <span>Download Official PDF Report</span>
          </a>
        </div>
      </div>

      {/* KPI Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card-industrial p-4">
          <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Total Visual Defects</div>
          <div className="text-2xl font-bold font-mono text-white mt-1">
            {totalDefects}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            {totalDefects === 0 ? 'Zero surface defects' : `${totalDefects} defect regions isolated`}
          </div>
        </div>

        <div className="card-industrial p-4">
          <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Inference Latency</div>
          <div className="text-2xl font-bold font-mono text-circuit-blue mt-1">
            {Number(inspection.inference_time).toFixed(1)} <span className="text-xs font-normal text-slate-400">ms</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            Ultralytics YOLO engine
          </div>
        </div>

        <div className="card-industrial p-4">
          <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Image Resolution</div>
          <div className="text-2xl font-bold font-mono text-slate-200 mt-1">
            {inspection.image_width && inspection.image_height
              ? `${inspection.image_width}×${inspection.image_height}`
              : '640×640'}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            Input surface dimensions
          </div>
        </div>

        <div className="card-industrial p-4">
          <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400">Confidence Threshold</div>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
            {Math.round((inspection.confidence_threshold || 0.25) * 100)}%
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            Model: {inspection.model_version || 'YOLO11n-PCB'}
          </div>
        </div>
      </div>

      {/* Dual Visual Inspection Canvas */}
      <div className="card-industrial p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-charcoal-700 gap-3">
          <div className="flex items-center gap-2">
            <Eye className="w-4 h-4 text-circuit-blue" />
            <h3 className="text-sm font-bold text-white tracking-wide">PCB Visual Inspection Canvas</h3>
          </div>

          {/* Mode Switcher */}
          <div className="flex items-center bg-navy-950 p-1 rounded-lg border border-charcoal-700 self-start sm:self-auto text-xs font-mono">
            <button
              onClick={() => setViewMode('annotated')}
              className={`px-3 py-1 rounded transition-colors ${
                viewMode === 'annotated'
                  ? 'bg-circuit-blue text-navy-950 font-bold shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Annotated Overlay
            </button>
            <button
              onClick={() => setViewMode('original')}
              className={`px-3 py-1 rounded transition-colors ${
                viewMode === 'original'
                  ? 'bg-circuit-blue text-navy-950 font-bold shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Raw PCB
            </button>
            <button
              onClick={() => setViewMode('split')}
              className={`px-3 py-1 rounded transition-colors ${
                viewMode === 'split'
                  ? 'bg-circuit-blue text-navy-950 font-bold shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Side-by-Side
            </button>
          </div>
        </div>

        {/* Display Canvas Container */}
        {viewMode === 'split' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Raw Input PCB</div>
              <div className="rounded-lg overflow-hidden bg-navy-950 border border-charcoal-700 aspect-square flex items-center justify-center p-2">
                <img
                  src={originalUrl}
                  alt="Raw PCB"
                  className="max-h-full max-w-full object-contain rounded"
                />
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-[11px] font-mono text-circuit-blue uppercase tracking-wider">AI Defect Localization</div>
              <div className="rounded-lg overflow-hidden bg-navy-950 border border-charcoal-700 aspect-square flex items-center justify-center p-2">
                <img
                  src={annotatedUrl || originalUrl}
                  alt="Annotated PCB"
                  className="max-h-full max-w-full object-contain rounded"
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-xl overflow-hidden bg-navy-950 border border-charcoal-700 max-h-[540px] flex items-center justify-center p-3 relative">
            <img
              src={viewMode === 'annotated' ? (annotatedUrl || originalUrl) : originalUrl}
              alt="PCB Inspection Display"
              className="max-h-[500px] w-auto object-contain rounded"
            />
            <div className="absolute bottom-4 left-4 bg-navy-950/80 backdrop-blur border border-charcoal-700 px-3 py-1 rounded text-[11px] font-mono text-slate-300">
              {viewMode === 'annotated' ? 'Displaying Neural Defect Overlay' : 'Displaying Raw Original Surface'}
            </div>
          </div>
        )}
      </div>

      {/* Detected Defects Table */}
      <div className="card-industrial p-5 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-charcoal-700">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-circuit-blue" />
            <h3 className="text-sm font-bold text-white tracking-wide">
              Isolated Surface Defects ({inspection.detections?.length || 0})
            </h3>
          </div>
          {Object.keys(categoryCounts).length > 0 && (
            <div className="flex flex-wrap gap-2 text-[11px] font-mono">
              {Object.entries(categoryCounts).map(([cName, count]) => (
                <span key={cName} className="px-2 py-0.5 bg-charcoal-800 border border-charcoal-700 rounded text-slate-300">
                  {cName}: <strong className="text-circuit-blue">{count}</strong>
                </span>
              ))}
            </div>
          )}
        </div>

        {(!inspection.detections || inspection.detections.length === 0) ? (
          <div className="p-8 text-center text-xs text-slate-400">
            <CheckCircle className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
            <p className="font-semibold text-slate-200">No surface defects detected</p>
            <p className="text-[11px] text-slate-500 mt-1">The PCB passed optical surface defect inspection within the specified threshold.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-charcoal-700 text-slate-400 text-[11px]">
                  <th className="pb-2.5 font-semibold">#</th>
                  <th className="pb-2.5 font-semibold">Defect Class</th>
                  <th className="pb-2.5 font-semibold">Confidence</th>
                  <th className="pb-2.5 font-semibold">Bounding Box [x1, y1, x2, y2]</th>
                  <th className="pb-2.5 font-semibold">Electrical Risk / Verification Advice</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-charcoal-800">
                {inspection.detections.map((det, index) => {
                  const isCritical = det.class_id === 0 || det.class_id === 2 || det.class_id === 3;
                  return (
                    <tr key={det.id || index} className="hover:bg-charcoal-800/40 transition-colors">
                      <td className="py-2.5 text-slate-500">{index + 1}</td>
                      <td className="py-2.5">
                        <span className="font-bold text-slate-200">{det.class_name}</span>
                        {isCritical && (
                          <span className="ml-2 px-1.5 py-0.2 bg-rose-500/20 text-rose-300 text-[10px] rounded border border-rose-500/30">
                            Critical
                          </span>
                        )}
                      </td>
                      <td className="py-2.5 text-circuit-blue font-bold">
                        {(det.confidence * 100).toFixed(1)}%
                      </td>
                      <td className="py-2.5 text-slate-400">
                        [{det.x1}, {det.y1}, {det.x2}, {det.y2}]
                      </td>
                      <td className="py-2.5 text-[11px] text-slate-300">
                        {det.class_id === 2 && 'Continuity / flying-probe test required'}
                        {det.class_id === 3 && 'Isolation resistance / hi-pot test required'}
                        {det.class_id === 0 && 'Drill coordinate optical check required'}
                        {det.class_id === 1 && '4-wire milliohm resistance check recommended'}
                        {det.class_id === 4 && 'Trace spacing clearance check (IPC-2221)'}
                        {det.class_id === 5 && 'Verify galvanic isolation from adjacent nets'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Mandatory Engineering Limitation & Electrical Boundary Notice */}
      <div className="p-4 bg-rose-950/20 border border-rose-500/30 rounded-xl space-y-2 text-xs">
        <div className="flex items-center gap-2 text-rose-400 font-bold uppercase tracking-wider text-[11px]">
          <ShieldAlert className="w-4 h-4 shrink-0" />
          <span>Critical Engineering Protocol: Optical Inspection Boundary</span>
        </div>
        <p className="text-slate-300 leading-relaxed text-[11px]">
          These findings represent <strong>visual defect predictions</strong> generated by an Ultralytics YOLO object detection neural network on optical surface imagery. Visual inspection cannot conclusively diagnose electrical functional state (internal continuity, galvanic isolation, or component values). Always confirm visual anomalies with standard electrical instrumentation (digital multimeter continuity, 4-wire Kelvin micro-ohmmeter, and high-voltage insulation hi-pot testing).
        </p>
      </div>
    </div>
  );
}
