import React from 'react';
import { Cpu, ShieldCheck, BookOpen, ExternalLink, GraduationCap, CheckCircle2 } from 'lucide-react';
import DisclaimerBanner from '../components/DisclaimerBanner';

export default function About() {
  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-wide">About CircuitDoctor</h2>
        <p className="text-xs text-slate-400 mt-0.5">
          AI-Powered PCB Surface Defect Inspection Platform &bull; Electronics & Communication Engineering
        </p>
      </div>

      <DisclaimerBanner />

      <div className="card-industrial p-6 space-y-5">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-lg bg-circuit-blue/10 border border-circuit-blue/30 flex items-center justify-center text-circuit-blue shrink-0">
            <Cpu className="w-7 h-7" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Engineering Background & Purpose</h3>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              Printed Circuit Boards (PCBs) form the physical backbone of all modern electronics. During etching, drilling,
              and plating manufacturing phases, microscopic surface defects frequently emerge: missing vias, trace necking (mouse bites),
              full trace fractures (opens), copper bridges (shorts), pin spurs, and residual copper flecks.
            </p>
            <p className="text-xs text-slate-300 mt-2 leading-relaxed">
              CircuitDoctor pairs deep computer vision with domain-specific electronics engineering knowledge, automating
              the visual identification, localization, and classification of these anomalies while advising on proper
              electrical verification protocols.
            </p>
          </div>
        </div>

        {/* Technical Architecture Stack */}
        <div className="pt-4 border-t border-charcoal-700">
          <h4 className="text-xs font-mono font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Technology Stack & Architecture
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 font-mono text-xs">
            <div className="p-3 bg-navy-950 rounded border border-charcoal-800">
              <span className="text-circuit-blue block font-bold font-sans">Frontend</span>
              <span className="text-slate-300 text-[11px] block mt-1">React 18 &bull; Vite &bull; Tailwind CSS &bull; Recharts &bull; Axios</span>
            </div>
            <div className="p-3 bg-navy-950 rounded border border-charcoal-800">
              <span className="text-circuit-cyan block font-bold font-sans">Backend</span>
              <span className="text-slate-300 text-[11px] block mt-1">Python 3.11 &bull; FastAPI &bull; Uvicorn &bull; SQLite &bull; SQLAlchemy</span>
            </div>
            <div className="p-3 bg-navy-950 rounded border border-charcoal-800">
              <span className="text-emerald-400 block font-bold font-sans">Computer Vision & AI</span>
              <span className="text-slate-300 text-[11px] block mt-1">PyTorch &bull; Ultralytics YOLO26n &bull; OpenCV &bull; Pillow</span>
            </div>
          </div>
        </div>

        {/* Visual vs Electrical Distinction */}
        <div className="pt-4 border-t border-charcoal-700 space-y-2">
          <h4 className="text-xs font-mono font-semibold text-slate-400 uppercase tracking-wider">
            Critical Domain Principle: Visual Detection vs. Electrical Diagnosis
          </h4>
          <p className="text-xs text-slate-300 leading-relaxed">
            In electronic hardware engineering, optical surface inspection cannot replace electrical characterization.
            A narrow gap between conductors may appear broken visually yet still conduct through buried copper vias; conversely,
            a trace with complete optical continuity might suffer internal delamination or high-resistance necking.
            CircuitDoctor strictly characterizes its outputs as visual predictions and integrates actionable recommendations
            for electrical continuity, 4-wire Kelvin resistance, and high-pot isolation testing.
          </p>
        </div>
      </div>
    </div>
  );
}
