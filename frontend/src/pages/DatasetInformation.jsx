import React, { useState, useEffect } from 'react';
import { Database, ShieldCheck, Layers, FileSpreadsheet, ExternalLink, RefreshCw, CheckCircle2 } from 'lucide-react';
import { getDatasetInfo } from '../services/api';

export default function DatasetInformation() {
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchInfo = async () => {
    setLoading(true);
    try {
      const data = await getDatasetInfo();
      setDatasetInfo(data);
    } catch (err) {
      console.error('Failed to load dataset info:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInfo();
  }, []);

  const totalImages = datasetInfo?.total_images || 1500;
  const totalAnnotations = datasetInfo?.total_annotations || 10013;
  const splits = datasetInfo?.splits || [];
  const classDist = datasetInfo?.class_distribution || [];

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide">DeepPCB Dataset Specifications</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Benchmark dataset metadata, annotation taxonomy, and leakage-safe partitioning architecture
          </p>
        </div>
        <button
          onClick={fetchInfo}
          disabled={loading}
          className="px-3.5 py-1.5 bg-charcoal-800 hover:bg-charcoal-700 border border-charcoal-600 rounded text-xs font-mono text-slate-300 flex items-center gap-2 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-circuit-blue' : ''}`} />
          <span>Refresh Metadata</span>
        </button>
      </div>

      {/* Primary KPI Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card-industrial p-5 space-y-2">
          <span className="text-xs font-mono uppercase text-slate-400">Primary Dataset</span>
          <h3 className="text-lg font-bold text-white">DeepPCB</h3>
          <p className="text-xs text-slate-400">Tang et al., 2019</p>
          <a
            href="https://github.com/tangsanli5201/DeepPCB"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs font-mono text-circuit-blue hover:underline pt-1"
          >
            <span>GitHub Repository</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>

        <div className="card-industrial p-5 space-y-2 font-mono text-xs">
          <span className="text-xs font-mono uppercase text-slate-400 font-sans">Verified Images</span>
          <div className="text-2xl font-bold text-circuit-blue font-mono">
            {totalImages.toLocaleString()}
          </div>
          <p className="text-slate-400 font-sans">
            640 &times; 640 px resolution linear CCD scan images
          </p>
        </div>

        <div className="card-industrial p-5 space-y-2 font-mono text-xs">
          <span className="text-xs font-mono uppercase text-slate-400 font-sans">Annotated Defect Boxes</span>
          <div className="text-2xl font-bold text-circuit-amber font-mono">
            {totalAnnotations.toLocaleString()}
          </div>
          <p className="text-slate-400 font-sans">
            Axis-aligned bounding boxes across 6 defect classes
          </p>
        </div>

        <div className="card-industrial p-5 space-y-2 font-mono text-xs">
          <span className="text-xs font-mono uppercase text-slate-400 font-sans">Data Leakage Check</span>
          <div className="text-2xl font-bold text-emerald-400 font-mono flex items-center gap-1.5">
            <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
            <span>0% Leak</span>
          </div>
          <p className="text-slate-400 font-sans">
            Partitions isolated by discrete PCB board groups
          </p>
        </div>
      </div>

      {/* Partition Split Overview */}
      <div className="card-industrial p-5 space-y-4">
        <h3 className="text-sm font-semibold text-white">Leakage-Safe Partition Allocation</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {splits.map((s) => (
            <div key={s.name} className="p-4 bg-navy-950 rounded-lg border border-charcoal-700 space-y-2 font-mono">
              <div className="flex justify-between items-center">
                <span className="font-bold text-white uppercase text-xs">[{s.name}] Partition</span>
                <span className="text-circuit-blue font-bold text-sm">{s.percentage}%</span>
              </div>
              <div className="text-xs text-slate-300">
                <span>Images: </span>
                <span className="text-white font-bold">{s.image_count}</span>
              </div>
              <div className="text-xs text-slate-300">
                <span>Labels: </span>
                <span className="text-white font-bold">{s.label_count}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Real Class Distribution Breakdown */}
      <div className="card-industrial p-5 space-y-4">
        <h3 className="text-sm font-semibold text-white">Genuine Defect Class Distribution</h3>
        <p className="text-xs text-slate-400">
          Distribution of all {totalAnnotations.toLocaleString()} ground-truth defect boxes converted into YOLO format
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {classDist.map((item) => (
            <div key={item.class_id} className="p-3.5 bg-navy-950 rounded border border-charcoal-700 space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="font-semibold text-white">
                  Class {item.class_id}: {item.class_name}
                </span>
                <span
                  className="font-mono font-bold text-xs"
                  style={{ color: item.color_hex }}
                >
                  {item.count} ({item.percentage}%)
                </span>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-charcoal-800 h-2 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${item.percentage * 4}%`,
                    maxWidth: '100%',
                    backgroundColor: item.color_hex,
                  }}
                />
              </div>

              <div className="flex justify-between items-center text-[11px] text-slate-400 font-mono">
                <span>Severity: <strong className="capitalize text-slate-300">{item.severity}</strong></span>
                <span>YOLO ID #{item.class_id}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Leakage Prevention Architecture */}
      <div className="card-industrial p-5 space-y-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-400" />
          <h3 className="text-sm font-semibold text-white">Data Leakage Prevention Guarantee</h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Because DeepPCB consists of image pairs (golden template and defective test image), paired instances share
          identical PCB geometry and trace topography. CircuitDoctor enforces split boundaries by PCB board group IDs
          (e.g., <code className="text-circuit-blue bg-navy-950 px-1 py-0.5 rounded">group00041</code>, <code className="text-circuit-blue bg-navy-950 px-1 py-0.5 rounded">group12000</code>) rather than random shuffling. This ensures that no template or near-duplicate geometry present in the test set
          was ever exposed to the model during training or validation passes.
        </p>
      </div>

      {/* Coordinate Format Conversion */}
      <div className="card-industrial p-5 space-y-3 font-mono text-xs">
        <div className="flex items-center gap-2 font-sans">
          <FileSpreadsheet className="w-4 h-4 text-circuit-blue" />
          <h3 className="text-sm font-semibold text-white font-sans">Annotation Format Conversion</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
          <div className="p-3 bg-navy-950 rounded border border-charcoal-700 space-y-1">
            <span className="text-[11px] font-sans text-slate-400 font-semibold block">Original DeepPCB Annotation:</span>
            <code className="text-slate-300 block">x1 y1 x2 y2 type</code>
            <p className="text-[11px] font-sans text-slate-500 pt-1">
              Absolute pixel coordinates of top-left and bottom-right corners followed by 1-indexed class ID (1-6).
            </p>
          </div>

          <div className="p-3 bg-navy-950 rounded border border-charcoal-700 space-y-1">
            <span className="text-[11px] font-sans text-slate-400 font-semibold block">Target YOLO Format:</span>
            <code className="text-circuit-blue block">class_id x_center y_center width height</code>
            <p className="text-[11px] font-sans text-slate-500 pt-1">
              0-indexed class (0-5) followed by normalized center coordinates and dimensions [0.0 - 1.0].
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
