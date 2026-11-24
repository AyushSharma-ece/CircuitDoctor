import React from 'react';
import { Shield, Cpu, RefreshCw } from 'lucide-react';
import DisclaimerBanner from './DisclaimerBanner';

export default function Header({ title, onRefresh, isRefreshing }) {
  return (
    <header className="h-16 bg-navy-900 border-b border-charcoal-700 px-6 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold text-white tracking-wide">{title}</h2>
        <div className="hidden md:block">
          <DisclaimerBanner compact={true} />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="p-2 text-slate-400 hover:text-circuit-blue hover:bg-charcoal-800 rounded-md transition-all disabled:opacity-50"
          title="Refresh Data"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-circuit-blue' : ''}`} />
        </button>

        <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-charcoal-800 border border-charcoal-600 rounded text-xs font-mono text-slate-300">
          <Cpu className="w-3.5 h-3.5 text-circuit-blue" />
          <span>INDUSTRIAL AOI</span>
        </div>
      </div>
    </header>
  );
}
