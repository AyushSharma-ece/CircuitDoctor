import React from 'react';
import { Cpu, HardDrive, ShieldCheck, AlertCircle, FileCode, Sliders, Activity, Layers, Clock } from 'lucide-react';

export default function ModelInformation({ modelInfo, health }) {
  const isModelReady = health?.model_status === 'ready' || modelInfo?.model_status === 'ready';
  const metrics = modelInfo?.training_metrics;
  const summary = metrics?.summary;
  const perClass = metrics?.per_class;
  const speed = metrics?.speed;

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-wide">YOLO Model Information & Telemetry</h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Deep learning model architecture specifications, hardware acceleration, and rigorous test partition metrics
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Core Architecture Card */}
        <div className="card-industrial p-5 space-y-4">
          <div className="flex items-center gap-3 pb-3 border-b border-charcoal-700">
            <Cpu className="w-5 h-5 text-circuit-blue" />
            <h3 className="text-sm font-semibold text-white">Neural Network Architecture</h3>
          </div>

          <div className="space-y-2.5 font-mono text-xs">
            <div className="flex justify-between py-1 border-b border-charcoal-800">
              <span className="text-slate-400">Model Name:</span>
              <span className="text-white font-bold">{modelInfo?.model_name || 'CircuitDoctor-YOLO'}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-charcoal-800">
              <span className="text-slate-400">Base Architecture:</span>
              <span className="text-circuit-blue">{modelInfo?.model_architecture || 'Ultralytics YOLO11n / YOLO26n'}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-charcoal-800">
              <span className="text-slate-400">Target Resolution:</span>
              <span className="text-white">640 &times; 640 pixels</span>
            </div>
            <div className="flex justify-between py-1 border-b border-charcoal-800">
              <span className="text-slate-400">Number of Classes:</span>
              <span className="text-white font-bold">6 DeepPCB Defect Classes</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Model Status:</span>
              <span className={`font-bold uppercase ${isModelReady ? 'text-emerald-400' : 'text-amber-400'}`}>
                {modelInfo?.model_status || health?.model_status || 'NOT LOADED'}
              </span>
            </div>
          </div>
        </div>

        {/* Compute & Hardware Accelerator Card */}
        <div className="card-industrial p-5 space-y-4">
          <div className="flex items-center gap-3 pb-3 border-b border-charcoal-700">
            <HardDrive className="w-5 h-5 text-circuit-cyan" />
            <h3 className="text-sm font-semibold text-white">Hardware Acceleration & Weights</h3>
          </div>

          <div className="space-y-2.5 font-mono text-xs">
            <div className="flex justify-between py-1 border-b border-charcoal-800">
              <span className="text-slate-400">Selected Device:</span>
              <span className="text-circuit-blue font-bold uppercase">{modelInfo?.device || health?.device || 'CPU'}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-charcoal-800">
              <span className="text-slate-400">CUDA Acceleration:</span>
              <span className={modelInfo?.cuda_available ? 'text-emerald-400' : 'text-slate-400'}>
                {modelInfo?.cuda_available ? 'Available & Detected' : 'Disabled (CPU mode)'}
              </span>
            </div>
            {modelInfo?.gpu_name && (
              <div className="flex justify-between py-1 border-b border-charcoal-800">
                <span className="text-slate-400">GPU Device:</span>
                <span className="text-white truncate max-w-[200px]">{modelInfo.gpu_name}</span>
              </div>
            )}
            <div className="flex justify-between py-1 border-b border-charcoal-800">
              <span className="text-slate-400">Model Weights Path:</span>
              <span className="text-slate-300 truncate max-w-[220px]" title={modelInfo?.model_path}>
                {modelInfo?.model_path || 'models/best.pt'}
              </span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Weights File Exists:</span>
              <span className={modelInfo?.weights_exist ? 'text-emerald-400' : 'text-amber-400'}>
                {modelInfo?.weights_exist ? 'Yes (best.pt ready)' : 'No (Pending Training)'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Actual Model Evaluation Metrics Section */}
      <div className="card-industrial p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-charcoal-700 gap-2">
          <div>
            <h3 className="text-sm font-semibold text-white">Evaluation Metrics on Untouched Test Partition</h3>
            <p className="text-xs text-slate-400">
              Evaluated strictly on DeepPCB test split (112 unseen images, 693 defect instances) to ensure zero data leakage
            </p>
          </div>
          {metrics?.evaluation_timestamp && (
            <span className="text-[11px] font-mono text-slate-500">
              Evaluated: {new Date(metrics.evaluation_timestamp).toLocaleString()}
            </span>
          )}
        </div>

        {summary ? (
          <div className="space-y-6">
            {/* KPI Metrics Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 font-mono text-xs">
              <div className="p-3 bg-navy-950 rounded border border-charcoal-700">
                <span className="text-slate-500 block text-[11px]">mAP@50</span>
                <span className="text-xl font-bold text-circuit-blue mt-0.5 block">
                  {(summary.mAP50 * 100).toFixed(1)}%
                </span>
                <span className="text-[10px] text-slate-500">IoU threshold 0.50</span>
              </div>
              <div className="p-3 bg-navy-950 rounded border border-charcoal-700">
                <span className="text-slate-500 block text-[11px]">mAP@50-95</span>
                <span className="text-xl font-bold text-emerald-400 mt-0.5 block">
                  {(summary.mAP50_95 * 100).toFixed(1)}%
                </span>
                <span className="text-[10px] text-slate-500">COCO stringent metric</span>
              </div>
              <div className="p-3 bg-navy-950 rounded border border-charcoal-700">
                <span className="text-slate-500 block text-[11px]">Mean Precision</span>
                <span className="text-xl font-bold text-white mt-0.5 block">
                  {(summary.mean_precision * 100).toFixed(1)}%
                </span>
                <span className="text-[10px] text-slate-500">Detection precision</span>
              </div>
              <div className="p-3 bg-navy-950 rounded border border-charcoal-700">
                <span className="text-slate-500 block text-[11px]">Mean Recall</span>
                <span className="text-xl font-bold text-white mt-0.5 block">
                  {(summary.mean_recall * 100).toFixed(1)}%
                </span>
                <span className="text-[10px] text-slate-500">Defect coverage rate</span>
              </div>
              <div className="p-3 bg-navy-950 rounded border border-charcoal-700">
                <span className="text-slate-500 block text-[11px]">Inference Latency</span>
                <span className="text-xl font-bold text-amber-400 mt-0.5 block">
                  {speed?.inference_ms ? `${speed.inference_ms} ms` : 'N/A'}
                </span>
                <span className="text-[10px] text-slate-500">Per 640×640 image</span>
              </div>
            </div>

            {/* Per-Class Breakdown Table */}
            {perClass && (
              <div className="space-y-2">
                <h4 className="text-xs font-semibold font-mono text-slate-300 uppercase tracking-wider">
                  Per-Class Defect Performance Breakdown
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead className="bg-navy-950 text-slate-400 text-[10px] uppercase border-b border-charcoal-700">
                      <tr>
                        <th className="py-2 px-3">Class ID</th>
                        <th className="py-2 px-3">Defect Category</th>
                        <th className="py-2 px-3">mAP@50</th>
                        <th className="py-2 px-3">mAP@50-95</th>
                        <th className="py-2 px-3">Precision</th>
                        <th className="py-2 px-3">Recall</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-charcoal-800 text-slate-300">
                      {Object.values(perClass).map((c) => (
                        <tr key={c.class_id} className="hover:bg-charcoal-800/40">
                          <td className="py-2 px-3 text-slate-500">Class {c.class_id}</td>
                          <td className="py-2 px-3 font-bold text-white">{c.class_name}</td>
                          <td className="py-2 px-3 text-circuit-blue font-bold">{(c.map50 * 100).toFixed(1)}%</td>
                          <td className="py-2 px-3 text-emerald-400">{(c.map50_95 * 100).toFixed(1)}%</td>
                          <td className="py-2 px-3">{(c.precision * 100).toFixed(1)}%</td>
                          <td className="py-2 px-3">{(c.recall * 100).toFixed(1)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="p-6 bg-navy-950/60 border border-charcoal-800 rounded-lg text-center space-y-2">
            <AlertCircle className="w-8 h-8 text-slate-500 mx-auto" />
            <h4 className="text-xs font-mono font-semibold text-slate-300">Metrics In Processing / Awaiting Evaluation</h4>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              Evaluation metrics (Precision, Recall, mAP@50, mAP@50-95) are calculated strictly against real test samples once model training finishes.
            </p>
          </div>
        )}
      </div>

      {/* Supported Classes Reference Table */}
      <div className="card-industrial p-5 space-y-4">
        <h3 className="text-sm font-semibold text-white">Registered Defect Taxonomy & Recommended Testing</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-navy-950 text-slate-400 text-[10px] uppercase border-b border-charcoal-700">
              <tr>
                <th className="py-2 px-3">ID</th>
                <th className="py-2 px-3">Defect Name</th>
                <th className="py-2 px-3">Severity</th>
                <th className="py-2 px-3">Description</th>
                <th className="py-2 px-3">Recommended Electrical Verification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-charcoal-800 text-slate-300">
              {(modelInfo?.supported_classes || []).map((cls) => {
                const isCrit = cls.severity === 'critical';
                return (
                  <tr key={cls.id} className="hover:bg-charcoal-800/40">
                    <td className="py-2.5 px-3 font-bold text-circuit-blue">{cls.id}</td>
                    <td className="py-2.5 px-3 font-bold text-white">{cls.name}</td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        isCrit ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      }`}>
                        {cls.severity}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-300">{cls.description}</td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-400">{cls.verification_advice}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
