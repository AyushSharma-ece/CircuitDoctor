import React, { useState, useEffect } from 'react';
import { Search, Filter, Calendar, Trash2, Download, ExternalLink, AlertTriangle, Layers, RefreshCw, X } from 'lucide-react';
import { getInspections, getInspectionById, deleteInspection, getReportDownloadUrl } from '../services/api';
import InspectionResults from '../components/InspectionResults';

export default function InspectionHistory() {
  const [inspections, setInspections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedClass, setSelectedClass] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [activeInspection, setActiveInspection] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const fetchInspections = async () => {
    setLoading(true);
    try {
      const data = await getInspections({
        defect_class: selectedClass !== '' ? parseInt(selectedClass) : undefined,
        status: statusFilter || undefined,
      });
      setInspections(data || []);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInspections();
  }, [selectedClass, statusFilter]);

  const handleRowClick = async (insp) => {
    setLoadingDetail(true);
    try {
      const fullData = await getInspectionById(insp.id);
      setActiveInspection(fullData);
    } catch (err) {
      console.error('Failed to load full inspection details:', err);
      setActiveInspection(insp);
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm(`Confirm permanent deletion of Inspection #${id} and associated image records?`)) {
      return;
    }
    try {
      await deleteInspection(id);
      setInspections((prev) => prev.filter((i) => i.id !== id));
      if (activeInspection?.id === id) {
        setActiveInspection(null);
      }
    } catch (err) {
      alert(`Deletion failed: ${err.message}`);
    }
  };

  const filteredInspections = inspections.filter((i) =>
    i.original_filename?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    i.id.toString().includes(searchTerm)
  );

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide">Inspection History</h2>
          <p className="text-xs text-slate-400 mt-0.5">Audit log of all processed PCB optical scans and persistent defect records</p>
        </div>
        <button
          onClick={fetchInspections}
          disabled={loading}
          className="px-3.5 py-1.5 bg-charcoal-800 hover:bg-charcoal-700 border border-charcoal-600 rounded text-xs font-mono text-slate-300 flex items-center gap-2 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-circuit-blue' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="card-industrial p-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by filename or #ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-navy-950 border border-charcoal-700 rounded text-xs text-white placeholder-slate-500 focus:outline-none focus:border-circuit-blue"
          />
        </div>

        {/* Defect Class Filter */}
        <div>
          <select
            value={selectedClass}
            onChange={(e) => setSelectedClass(e.target.value)}
            className="w-full px-3 py-2 bg-navy-950 border border-charcoal-700 rounded text-xs text-slate-300 focus:outline-none focus:border-circuit-blue"
          >
            <option value="">All Defect Classes</option>
            <option value="0">Class 0: Missing Hole</option>
            <option value="1">Class 1: Mouse Bite</option>
            <option value="2">Class 2: Open Circuit</option>
            <option value="3">Class 3: Short</option>
            <option value="4">Class 4: Spur</option>
            <option value="5">Class 5: Spurious Copper</option>
          </select>
        </div>

        {/* Status Filter */}
        <div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-3 py-2 bg-navy-950 border border-charcoal-700 rounded text-xs text-slate-300 focus:outline-none focus:border-circuit-blue"
          >
            <option value="">All Visual Statuses</option>
            <option value="pass">Pass (0 Defects)</option>
            <option value="warning">Warning (Medium / Low Severity)</option>
            <option value="fail">Fail (Critical Defects Present)</option>
          </select>
        </div>
      </div>

      {/* Detail Inspection Modal View */}
      {activeInspection && (
        <div className="fixed inset-0 z-50 bg-navy-950/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-charcoal-900 border border-charcoal-700 rounded-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto p-6 relative shadow-2xl">
            <button
              onClick={() => setActiveInspection(null)}
              className="absolute top-4 right-4 p-2 text-slate-400 hover:text-white rounded-lg bg-charcoal-800 hover:bg-charcoal-700 transition-colors z-10"
              title="Close Detail View"
            >
              <X className="w-5 h-5" />
            </button>
            <InspectionResults inspection={activeInspection} onReset={() => setActiveInspection(null)} />
          </div>
        </div>
      )}

      {/* Main Table Feed */}
      <div className="card-industrial p-5">
        {loading ? (
          <div className="text-center py-16 text-slate-400 font-mono text-xs">
            Loading persistent records from SQLite...
          </div>
        ) : filteredInspections.length === 0 ? (
          <div className="text-center py-16">
            <Layers className="w-10 h-10 text-slate-600 mx-auto mb-2" />
            <p className="text-sm font-medium text-slate-400">No inspection records match filter criteria.</p>
            <p className="text-xs text-slate-500 mt-1">Adjust search parameters or upload new boards to inspect.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-navy-950 text-slate-400 font-mono uppercase text-[10px] tracking-wider border-b border-charcoal-700">
                <tr>
                  <th className="py-2.5 px-3">ID</th>
                  <th className="py-2.5 px-3">PCB Photograph</th>
                  <th className="py-2.5 px-3">Defect Counts</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Model</th>
                  <th className="py-2.5 px-3">Latency</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-charcoal-800 text-slate-300">
                {filteredInspections.map((insp) => (
                  <tr
                    key={insp.id}
                    onClick={() => handleRowClick(insp)}
                    className="hover:bg-charcoal-800/60 cursor-pointer transition-colors"
                  >
                    <td className="py-3 px-3 font-mono text-circuit-blue font-bold">#{insp.id}</td>
                    <td className="py-3 px-3">
                      <div className="font-medium text-white truncate max-w-[200px]">{insp.original_filename}</div>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-mono font-semibold ${
                        insp.total_defects > 0
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}>
                        {insp.total_defects} anomalies
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                        insp.inspection_status === 'pass'
                          ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20'
                          : insp.inspection_status === 'fail'
                          ? 'text-rose-400 bg-rose-500/10 border border-rose-500/20'
                          : 'text-amber-400 bg-amber-500/10 border border-amber-500/20'
                      }`}>
                        {insp.inspection_status}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-400">{insp.model_version}</td>
                    <td className="py-3 px-3 font-mono text-slate-400">{Number(insp.inference_time).toFixed(1)} ms</td>
                    <td className="py-3 px-3 text-slate-400">{new Date(insp.created_at).toLocaleString()}</td>
                    <td className="py-3 px-3 text-right space-x-2" onClick={(e) => e.stopPropagation()}>
                      <a
                        href={getReportDownloadUrl(insp.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block p-1.5 text-slate-400 hover:text-circuit-blue hover:bg-circuit-blue/10 rounded transition-colors"
                        title="Download PDF Report"
                      >
                        <Download className="w-3.5 h-3.5" />
                      </a>
                      <button
                        onClick={(e) => handleDelete(insp.id, e)}
                        className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded transition-colors"
                        title="Delete Inspection"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
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
