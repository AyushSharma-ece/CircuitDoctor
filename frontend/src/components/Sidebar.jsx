import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  ScanEye,
  History,
  BarChart3,
  Cpu,
  Database,
  Settings,
  Info,
  ShieldCheck,
  Activity,
  AlertCircle
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'New Inspection', path: '/inspect', icon: ScanEye },
  { name: 'Inspection History', path: '/history', icon: History },
  { name: 'Defect Analysis', path: '/analysis', icon: BarChart3 },
  { name: 'Model Information', path: '/model', icon: Cpu },
  { name: 'Dataset Information', path: '/dataset', icon: Database },
  { name: 'Settings', path: '/settings', icon: Settings },
  { name: 'About CircuitDoctor', path: '/about', icon: Info },
];

export default function Sidebar({ health, modelInfo }) {
  const isModelReady = health?.model_status === 'ready';
  const isHealthy = health?.status === 'healthy';

  return (
    <aside className="w-64 bg-navy-900 border-r border-charcoal-700 flex flex-col justify-between shrink-0 h-screen sticky top-0">
      {/* Brand Header */}
      <div>
        <div className="p-5 border-b border-charcoal-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-circuit-blue/10 border border-circuit-blue/30 flex items-center justify-center text-circuit-blue shadow-inner">
              <ScanEye className="w-6 h-6 text-circuit-blue animate-pulse" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-wide flex items-center gap-1.5">
                Circuit<span className="text-circuit-blue">Doctor</span>
              </h1>
              <p className="text-[11px] font-mono text-slate-400">PCB Inspection AI</p>
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-circuit-blue/15 text-circuit-blue border border-circuit-blue/30 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-charcoal-800'
                  }`
                }
              >
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Industrial Hardware Telemetry Footer */}
      <div className="p-4 border-t border-charcoal-700 bg-navy-950/70 space-y-2.5 text-xs font-mono">
        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
          <span>System Status</span>
          <span className="flex items-center gap-1">
            <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-emerald-500 animate-ping' : 'bg-amber-500'}`} />
            <span className={isHealthy ? 'text-emerald-400' : 'text-amber-400'}>
              {isHealthy ? 'ONLINE' : 'DEGRADED'}
            </span>
          </span>
        </div>

        <div className="space-y-1.5 pt-1 text-[11px]">
          <div className="flex justify-between items-center text-slate-400">
            <span>Model:</span>
            <span className={`font-semibold ${isModelReady ? 'text-emerald-400' : 'text-amber-400'}`}>
              {isModelReady ? 'READY' : 'UNLOADED'}
            </span>
          </div>

          <div className="flex justify-between items-center text-slate-400">
            <span>Device:</span>
            <span className="text-circuit-blue uppercase">
              {health?.device || 'CPU'}
            </span>
          </div>

          <div className="flex justify-between items-center text-slate-400">
            <span>Arch:</span>
            <span className="text-slate-300 truncate max-w-[120px]">
              {modelInfo?.model_architecture || 'YOLO26n'}
            </span>
          </div>
        </div>

        <div className="pt-2 border-t border-charcoal-800 flex items-center justify-between text-[10px] text-slate-500">
          <span>v1.0.0</span>
          <span>Tang et al. 2019</span>
        </div>
      </div>
    </aside>
  );
}
