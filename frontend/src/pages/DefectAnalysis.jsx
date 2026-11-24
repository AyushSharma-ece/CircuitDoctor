import React from 'react';
import { AlertOctagon, ShieldAlert, Cpu, CheckCircle2, AlertTriangle, Layers } from 'lucide-react';

const DEFECT_TAXONOMY = [
  {
    id: 0,
    name: 'Missing Hole',
    key: 'missing_hole',
    severity: 'critical',
    color: '#ef4444',
    description: 'Via or through-hole missing from required drill coordinate on the PCB substrate.',
    risk: 'Breaks interconnect between inner routing layers or prevents THT component lead mounting.',
    testing: 'Automated optical drill coordinate verification followed by flying-probe net continuity test.'
  },
  {
    id: 1,
    name: 'Mouse Bite',
    key: 'mouse_bite',
    severity: 'medium',
    color: '#f97316',
    description: 'Erosion or sharp bite-like nicks along conductive copper trace perimeters.',
    risk: 'Locally restricts cross-sectional conductor area, causing elevated resistance, I²R heating, and electromigration.',
    testing: 'Four-wire Kelvin resistance measurement across trace to detect localized impedance spikes.'
  },
  {
    id: 2,
    name: 'Open Circuit',
    key: 'open_circuit',
    severity: 'critical',
    color: '#dc2626',
    description: 'Unintended full fracture or separation across a conductive copper trace.',
    risk: 'Total signal discontinuity or power delivery failure along the affected net.',
    testing: 'Digital multimeter continuity test (0 ohm threshold) or in-circuit functional testing (ICT).'
  },
  {
    id: 3,
    name: 'Short',
    key: 'short',
    severity: 'critical',
    color: '#b91c1c',
    description: 'Inadvertent copper bridging connecting two electrically distinct conductor traces.',
    risk: 'Shorts power rails to ground, creates logic contention, or damages ICs during initial board power-up.',
    testing: 'High-potential (hi-pot) dielectric isolation test and netlist cross-short resistance checks.'
  },
  {
    id: 4,
    name: 'Spur',
    key: 'spur',
    severity: 'medium',
    color: '#eab308',
    description: 'Protruding copper appendage extending outwards towards adjacent traces.',
    risk: 'Violates IPC minimum trace clearance spacing rules; risks dielectric breakdown under high voltage or humidity.',
    testing: 'Optical coordinate distance verification against IPC-2221 design spacing requirements.'
  },
  {
    id: 5,
    name: 'Spurious Copper',
    key: 'spurious_copper',
    severity: 'low',
    color: '#38bdf8',
    description: 'Unconnected residual copper speck or island remaining on insulating laminate substrate.',
    risk: 'Creates parasitic capacitance or risks breaking loose as conductive FOD during vibration.',
    testing: 'Megohmmeter insulation resistance testing between island and nearest signal conductor.'
  }
];

export default function DefectAnalysis({ stats }) {
  const defectDist = stats?.defect_distribution || [];
  const countMap = {};
  defectDist.forEach((item) => {
    countMap[item.class_id] = item.count;
  });

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-wide">PCB Defect Taxonomy & Analysis</h2>
        <p className="text-xs text-slate-400 mt-0.5">
          Standardized 6 DeepPCB defect classifications with engineering risk and electrical verification protocols
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {DEFECT_TAXONOMY.map((defect) => {
          const detectedCount = countMap[defect.id] || 0;
          return (
            <div
              key={defect.id}
              className="card-industrial p-5 flex flex-col justify-between space-y-4 relative overflow-hidden"
            >
              <div
                className="absolute top-0 left-0 right-0 h-1"
                style={{ backgroundColor: defect.color }}
              />

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono px-2 py-0.5 rounded bg-charcoal-800 text-slate-300">
                      Class #{defect.id}
                    </span>
                    <h3 className="text-sm font-bold text-white">{defect.name}</h3>
                  </div>
                  <span
                    className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded ${
                      defect.severity === 'critical'
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        : defect.severity === 'medium'
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-circuit-blue/20 text-circuit-blue border border-circuit-blue/30'
                    }`}
                  >
                    {defect.severity}
                  </span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">
                  {defect.description}
                </p>
              </div>

              {/* Technical Engineering Impact */}
              <div className="p-3 bg-navy-950/70 border border-charcoal-800 rounded text-xs space-y-2">
                <div>
                  <span className="font-semibold text-rose-300 text-[11px] block">Electrical Risk:</span>
                  <span className="text-slate-400 text-[11px] leading-normal">{defect.risk}</span>
                </div>

                <div className="pt-2 border-t border-charcoal-800">
                  <span className="font-semibold text-circuit-blue text-[11px] block">Recommended Testing:</span>
                  <span className="text-slate-400 text-[11px] leading-normal">{defect.testing}</span>
                </div>
              </div>

              {/* Detected Frequency Stat */}
              <div className="pt-2 border-t border-charcoal-800 flex items-center justify-between font-mono text-xs">
                <span className="text-slate-400">Total Detections Logged:</span>
                <span className="font-bold text-white" style={{ color: detectedCount > 0 ? defect.color : '#94a3b8' }}>
                  {detectedCount}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
