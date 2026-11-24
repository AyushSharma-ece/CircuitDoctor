import React from 'react';
import { AlertTriangle, Cpu } from 'lucide-react';

export default function DisclaimerBanner({ compact = false }) {
  if (compact) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-500/10 border border-amber-500/20 rounded text-xs text-amber-300">
        <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
        <span>Optical Visual Detection Only &bull; Electrical confirmation recommended for shorts/opens.</span>
      </div>
    );
  }

  return (
    <div className="p-4 bg-navy-900 border border-amber-500/30 rounded-lg flex items-start gap-3.5 shadow-sm">
      <div className="p-2 bg-amber-500/10 rounded-md shrink-0 mt-0.5">
        <AlertTriangle className="w-5 h-5 text-amber-400" />
      </div>
      <div className="text-sm">
        <div className="font-semibold text-amber-300 flex items-center gap-2">
          <span>Important Technical & Safety Limitation</span>
          <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 bg-amber-400/20 text-amber-300 rounded font-bold">Advisory</span>
        </div>
        <p className="text-slate-300 mt-1 leading-relaxed text-xs">
          CircuitDoctor detects visible surface manufacturing anomalies using computer vision. Image-based deep learning
          <strong> cannot confirm </strong> internal copper layers, high-resistance opens, dielectric leakage, or component electrical health.
          Predicted visual defects must be confirmed through dedicated electrical tests (continuity, flying probe, or milliohm inspection).
        </p>
      </div>
    </div>
  );
}
