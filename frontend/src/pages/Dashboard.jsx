import React from 'react';
import { Link } from 'react-router-dom';
import {
  Scan,
  AlertOctagon,
  Clock,
  Layers,
  Cpu,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  FolderOpen,
  PlusCircle,
  HelpCircle
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import DisclaimerBanner from '../components/DisclaimerBanner';

export default function Dashboard({ stats, health, modelInfo, recentInspections, loading }) {
  const isModelReady = health?.model_status === 'ready';
  const totalInspections = stats?.total_inspections || 0;
  const totalDefects = stats?.total_defects_detected || 0;
  const avgLatency = stats?.average_inference_time_ms || 0;
  const defectDist = stats?.defect_distribution || [];

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Top Disclaimer Advisory */}
      <DisclaimerBanner />

      {/* Model Alert Banner if not loaded */}
      {!isModelReady && (
        <div className="p-4 bg-charcoal-900 border border-amber-500/40 rounded-lg flex items-center justify-between text-sm">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
            <div>
              <span className="font-semibold text-amber-300">Model Weights Notice: </span>
              <span className="text-slate-300">
                The YOLO model weights are currently <span className="font-mono text-amber-400 font-bold uppercase">{health?.model_status || 'NOT LOADED'}</span>.
                Inspect operations require trained weights at <code className="text-xs bg-navy-950 px-1 py-0.5 rounded text-circuit-blue">{health?.model_path || 'models/best.pt'}</code>.
              </span>
            </div>
          </div>
          <Link
            to="/model"
            className="px-3 py-1.5 bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 border border-amber-500/40 rounded text-xs font-mono font-medium transition-colors shrink-0"
          >
            Model Setup &rarr;
          </Link>
        </div>
      )}

      {/* Primary KPI Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Inspections */}
        <div className="card-industrial p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">Total Inspections</span>
            <Scan className="w-4 h-4 text-circuit-blue" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-white tracking-tight">
              {totalInspections}
            </span>
            <span className="text-xs text-slate-400">PCBs</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-400 flex items-center gap-1">
            <span className="text-emerald-400 font-mono font-semibold">{stats?.defect_free_inspections || 0}</span>
            <span>defect-free / </span>
            <span className="text-amber-400 font-mono font-semibold">{stats?.defective_inspections || 0}</span>
            <span>defective</span>
          </div>
        </div>

        {/* Total Detected Defects */}
        <div className="card-industrial p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">Detected Defects</span>
            <AlertOctagon className="w-4 h-4 text-circuit-amber" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-circuit-amber tracking-tight">
              {totalDefects}
            </span>
            <span className="text-xs text-slate-400">anomalies</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Across 6 DeepPCB defect classes
          </div>
        </div>

        {/* Avg Inference Latency */}
        <div className="card-industrial p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">Avg Inference Time</span>
            <Clock className="w-4 h-4 text-circuit-cyan" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-3xl font-bold font-mono text-white tracking-tight">
              {avgLatency > 0 ? avgLatency : '--'}
            </span>
            <span className="text-xs text-slate-400">{avgLatency > 0 ? 'ms' : 'no data'}</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-400">
            Measured execution duration
          </div>
        </div>

        {/* AI Model Status */}
        <div className="card-industrial p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-mono uppercase tracking-wider">Model Architecture</span>
            <Cpu className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-xl font-bold font-mono text-white truncate">
              {modelInfo?.model_architecture || 'YOLO26n'}
            </span>
          </div>
          <div className="mt-2 text-[11px] flex items-center justify-between">
            <span className="text-slate-400">Status:</span>
            <span className={`font-mono font-bold uppercase ${isModelReady ? 'text-emerald-400' : 'text-amber-400'}`}>
              {health?.model_status || 'NOT FOUND'}
            </span>
          </div>
        </div>
      </div>

      {/* Center Section: Defect Distribution Chart & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Defect Distribution Chart */}
        <div className="lg:col-span-2 card-industrial p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white tracking-wide">Defect Distribution</h3>
              <p className="text-xs text-slate-400">Cumulative count by manufacturing defect class</p>
            </div>
            <Link to="/analysis" className="text-xs font-mono text-circuit-blue hover:underline flex items-center gap-1">
              <span>View details</span>
              <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {totalDefects === 0 ? (
            <div className="h-64 flex flex-col items-center justify-center text-center border border-dashed border-charcoal-700 rounded-lg p-6">
              <FolderOpen className="w-10 h-10 text-slate-600 mb-2" />
              <p className="text-sm font-medium text-slate-400">No Defect Records Found</p>
              <p className="text-xs text-slate-500 max-w-sm mt-1">
                The database does not contain defect records yet. Perform an inspection to see real-time distribution charts.
              </p>
              <Link
                to="/inspect"
                className="mt-4 px-3.5 py-1.5 bg-circuit-blue text-navy-950 font-semibold text-xs rounded hover:bg-circuit-blue/90 transition-colors flex items-center gap-1.5"
              >
                <PlusCircle className="w-3.5 h-3.5" />
                <span>Start New Inspection</span>
              </Link>
            </div>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={defectDist} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                  <XAxis type="number" stroke="#64748b" fontSize={11} />
                  <YAxis type="category" dataKey="class_name" stroke="#94a3b8" fontSize={11} width={100} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '6px' }}
                    labelStyle={{ color: '#f8fafc', fontWeight: 'bold' }}
                    formatter={(val, name, item) => [`${val} (${item.payload.percentage}%)`, 'Detections']}
                  />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {defectDist.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color_hex || '#38bdf8'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Quick Launch & Hardware Telemetry */}
        <div className="space-y-4">
          {/* Quick Actions Panel */}
          <div className="card-industrial p-5">
            <h3 className="text-sm font-semibold text-white tracking-wide mb-3">Inspection Actions</h3>
            <div className="space-y-2">
              <Link
                to="/inspect"
                className="w-full flex items-center justify-between p-3 rounded bg-circuit-blue/10 hover:bg-circuit-blue/20 border border-circuit-blue/30 text-circuit-blue text-sm font-medium transition-all group"
              >
                <span className="flex items-center gap-2">
                  <Scan className="w-4 h-4" />
                  <span>New Optical Inspection</span>
                </span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>

              <Link
                to="/history"
                className="w-full flex items-center justify-between p-3 rounded bg-charcoal-800 hover:bg-charcoal-700 border border-charcoal-600 text-slate-300 text-sm font-medium transition-all group"
              >
                <span className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-slate-400" />
                  <span>Browse Inspection History</span>
                </span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>

          {/* Hardware & Environment Telemetry */}
          <div className="card-industrial p-5 space-y-3 font-mono text-xs">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider font-sans">
              Runtime Telemetry
            </h3>
            <div className="space-y-2 divide-y divide-charcoal-800 text-slate-300">
              <div className="flex justify-between pt-1">
                <span className="text-slate-400">Compute Backend:</span>
                <span className="text-circuit-blue font-bold uppercase">{health?.device || 'CPU'}</span>
              </div>
              <div className="flex justify-between pt-2">
                <span className="text-slate-400">Database Engine:</span>
                <span className="text-slate-200">SQLite (SQLAlchemy)</span>
              </div>
              <div className="flex justify-between pt-2">
                <span className="text-slate-400">Target Resolution:</span>
                <span className="text-slate-200">640 &times; 640 px</span>
              </div>
              <div className="flex justify-between pt-2">
                <span className="text-slate-400">Default Confidence:</span>
                <span className="text-slate-200">25% (0.25)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Inspections Table Feed */}
      <div className="card-industrial p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white tracking-wide">Recent Inspections</h3>
            <p className="text-xs text-slate-400">Log of recent automated optical scans</p>
          </div>
          <Link to="/history" className="text-xs font-mono text-circuit-blue hover:underline flex items-center gap-1">
            <span>View all ({totalInspections})</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        {recentInspections?.length === 0 ? (
          <div className="text-center py-10 border border-dashed border-charcoal-700 rounded-lg">
            <p className="text-sm text-slate-400">No inspections logged in database.</p>
            <p className="text-xs text-slate-500 mt-1">Upload an image from the New Inspection page to begin.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-navy-950 text-slate-400 font-mono uppercase text-[10px] tracking-wider border-b border-charcoal-700">
                <tr>
                  <th className="py-2.5 px-3">ID</th>
                  <th className="py-2.5 px-3">Filename</th>
                  <th className="py-2.5 px-3">Defects</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Latency</th>
                  <th className="py-2.5 px-3">Date</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-charcoal-800 text-slate-300">
                {recentInspections?.map((insp) => (
                  <tr key={insp.id} className="hover:bg-charcoal-800/50 transition-colors">
                    <td className="py-3 px-3 font-mono text-circuit-blue">#{insp.id}</td>
                    <td className="py-3 px-3 font-medium text-white truncate max-w-[180px]">
                      {insp.original_filename}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-mono font-semibold ${
                        insp.total_defects > 0
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}>
                        {insp.total_defects} {insp.total_defects === 1 ? 'defect' : 'defects'}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className="capitalize">{insp.inspection_status}</span>
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-400">
                      {Math.round(insp.inference_time * 1000)} ms
                    </td>
                    <td className="py-3 px-3 text-slate-400">
                      {new Date(insp.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <Link
                        to={`/history?id=${insp.id}`}
                        className="text-circuit-blue hover:underline font-mono text-xs"
                      >
                        Details &rarr;
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
