import React, { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, X, AlertTriangle, CheckCircle, Cpu, Loader2 } from 'lucide-react';
import { uploadAndInspect } from '../services/api';
import DisclaimerBanner from '../components/DisclaimerBanner';
import InspectionResults from '../components/InspectionResults';

export default function NewInspection({ health, onInspectionCompleted }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.25);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  const isModelReady = health?.model_status === 'ready';

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    validateAndSelectFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    validateAndSelectFile(file);
  };

  const validateAndSelectFile = (file) => {
    if (!file) return;
    setError(null);
    setResult(null);

    const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
      setError('Unsupported file type. Please upload a standard JPG, JPEG, or PNG PCB image.');
      return;
    }

    const maxSizeMb = 25;
    if (file.size > maxSizeMb * 1024 * 1024) {
      setError(`File size exceeds ${maxSizeMb}MB maximum limit.`);
      return;
    }

    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleRemoveImage = () => {
    setSelectedFile(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    setError(null);
    setResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleReset = () => {
    handleRemoveImage();
    setResult(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;
    setAnalyzing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('confidence_threshold', confidenceThreshold.toString());

    try {
      const res = await uploadAndInspect(formData);
      setResult(res);
      if (onInspectionCompleted) {
        onInspectionCompleted();
      }
    } catch (err) {
      setError(err.message || 'Inspection inference failed.');
    } finally {
      setAnalyzing(false);
    }
  };

  // If inspection results are available, render interactive results view
  if (result) {
    return (
      <div className="p-6 max-w-6xl mx-auto">
        <InspectionResults inspection={result} onReset={handleReset} />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide">Automated Optical Inspection</h2>
          <p className="text-xs text-slate-400 mt-0.5">Upload a high-resolution surface PCB image for defect analysis</p>
        </div>
      </div>

      <DisclaimerBanner />

      {error && (
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-lg text-xs text-rose-300 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Upload / Preview Area */}
      <div className="card-industrial p-6 space-y-6">
        {!previewUrl ? (
          <div
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-charcoal-600 hover:border-circuit-blue/60 rounded-xl p-12 text-center cursor-pointer transition-all bg-navy-950/40 hover:bg-navy-950/80 group"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".jpg,.jpeg,.png"
              className="hidden"
            />
            <div className="w-16 h-16 rounded-full bg-charcoal-800 border border-charcoal-600 flex items-center justify-center mx-auto text-slate-400 group-hover:text-circuit-blue group-hover:scale-110 transition-all">
              <UploadCloud className="w-8 h-8" />
            </div>
            <h3 className="mt-4 text-sm font-semibold text-white">Drag & drop PCB photograph here</h3>
            <p className="mt-1 text-xs text-slate-400">or click to browse local files</p>
            <div className="mt-4 flex items-center justify-center gap-2 text-[11px] font-mono text-slate-500">
              <span className="px-2 py-0.5 bg-charcoal-800 rounded">JPG</span>
              <span className="px-2 py-0.5 bg-charcoal-800 rounded">PNG</span>
              <span className="px-2 py-0.5 bg-charcoal-800 rounded">Max 25 MB</span>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-charcoal-700">
              <div className="flex items-center gap-2">
                <ImageIcon className="w-4 h-4 text-circuit-blue" />
                <span className="text-xs font-mono font-medium text-slate-200">{selectedFile?.name}</span>
                <span className="text-[11px] text-slate-500 font-mono">
                  ({(selectedFile?.size / (1024 * 1024)).toFixed(2)} MB)
                </span>
              </div>
              <button
                onClick={handleRemoveImage}
                disabled={analyzing}
                className="p-1 text-slate-400 hover:text-rose-400 rounded transition-colors disabled:opacity-50"
                title="Remove Image"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Image Preview Box */}
            <div className="relative rounded-lg overflow-hidden bg-navy-950 border border-charcoal-700 max-h-[460px] flex items-center justify-center">
              <img
                src={previewUrl}
                alt="PCB Preview"
                className="max-h-[440px] w-auto object-contain rounded"
              />
            </div>
          </div>
        )}

        {/* Inference Controls */}
        <div className="pt-4 border-t border-charcoal-700 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="w-full sm:w-72 space-y-1">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-slate-400">Confidence Threshold:</span>
              <span className="text-circuit-blue font-bold">{Math.round(confidenceThreshold * 100)}%</span>
            </div>
            <input
              type="range"
              min="0.10"
              max="0.90"
              step="0.05"
              value={confidenceThreshold}
              onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
              disabled={analyzing}
              className="w-full accent-circuit-blue bg-charcoal-800 rounded h-1.5 cursor-pointer"
            />
          </div>

          <button
            onClick={handleAnalyze}
            disabled={!selectedFile || analyzing}
            className="w-full sm:w-auto px-6 py-2.5 bg-circuit-blue hover:bg-circuit-blue/90 text-navy-950 font-bold text-xs rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-md"
          >
            {analyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Running YOLO Neural Inspection...</span>
              </>
            ) : (
              <>
                <Cpu className="w-4 h-4" />
                <span>Analyse PCB Surface</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
