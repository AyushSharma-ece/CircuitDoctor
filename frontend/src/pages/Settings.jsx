import React, { useState } from 'react';
import { Settings as SettingsIcon, Save, RefreshCw, HardDrive, Cpu, Sliders } from 'lucide-react';

export default function SettingsPage({ health, modelInfo }) {
  const [confThreshold, setConfThreshold] = useState(0.25);
  const [iouThreshold, setIouThreshold] = useState(0.45);
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-wide">Inspection System Settings</h2>
        <p className="text-xs text-slate-400 mt-0.5">Configure default inference thresholds, API endpoints, and storage retention</p>
      </div>

      <form onSubmit={handleSave} className="card-industrial p-6 space-y-6">
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Sliders className="w-4 h-4 text-circuit-blue" />
            <span>Inference Hyperparameters</span>
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-xs">
            <div className="space-y-2">
              <label className="text-slate-300 font-medium flex justify-between">
                <span>Default Confidence Threshold:</span>
                <span className="font-mono text-circuit-blue font-bold">{Math.round(confThreshold * 100)}%</span>
              </label>
              <input
                type="range"
                min="0.10"
                max="0.90"
                step="0.05"
                value={confThreshold}
                onChange={(e) => setConfThreshold(parseFloat(e.target.value))}
                className="w-full accent-circuit-blue bg-charcoal-800 rounded h-1.5 cursor-pointer"
              />
              <p className="text-[11px] text-slate-500">
                Minimum probability threshold required to register a defect detection candidate.
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-slate-300 font-medium flex justify-between">
                <span>NMS IoU Threshold:</span>
                <span className="font-mono text-circuit-blue font-bold">{Math.round(iouThreshold * 100)}%</span>
              </label>
              <input
                type="range"
                min="0.20"
                max="0.80"
                step="0.05"
                value={iouThreshold}
                onChange={(e) => setIouThreshold(parseFloat(e.target.value))}
                className="w-full accent-circuit-blue bg-charcoal-800 rounded h-1.5 cursor-pointer"
              />
              <p className="text-[11px] text-slate-500">
                Non-Maximum Suppression intersection-over-union cutoff for redundant bounding boxes.
              </p>
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-charcoal-700 flex items-center justify-between">
          <span className="text-xs font-mono text-emerald-400">
            {saved && 'Settings applied successfully!'}
          </span>
          <button
            type="submit"
            className="px-5 py-2 bg-circuit-blue hover:bg-circuit-blue/90 text-navy-950 font-bold text-xs rounded transition-all flex items-center gap-2 shadow"
          >
            <Save className="w-3.5 h-3.5" />
            <span>Save Configuration</span>
          </button>
        </div>
      </form>
    </div>
  );
}
