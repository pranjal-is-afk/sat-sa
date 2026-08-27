import { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileType, CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';
import { uploadFiles, runAnalysis } from '../api';
import ErrorBanner from '../components/ErrorBanner';

export default function UploadPage({ onBatchReady }) {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [analysing, setAnalysing] = useState(false);
  
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setIsDragging(true);
    else if (e.type === 'dragleave') setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFiles(prev => [...prev, ...Array.from(e.dataTransfer.files)]);
    }
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(prev => [...prev, ...Array.from(e.target.files)]);
    }
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    setError(null);
    setProgress(0);
    
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    try {
      const res = await uploadFiles(formData, (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setProgress(percentCompleted);
      });
      setSummary(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleRunAnalysis = async () => {
    if (!summary?.batch_id) return;
    
    setAnalysing(true);
    setError(null);
    
    try {
      await runAnalysis(summary.batch_id);
      onBatchReady(summary.batch_id);
      navigate('/overview');
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Analysis failed');
      setAnalysing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 mt-8">
      <h1 className="text-3xl font-bold mb-2">Ingest Data</h1>
      <p className="text-slate-400 mb-8">Upload CSE alerts, cases, and asset inventory data for analysis.</p>
      
      <ErrorBanner message={error} onDismiss={() => setError(null)} />
      
      {!summary ? (
        <div className="space-y-6">
          <div 
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors cursor-pointer ${
              isDragging ? 'border-blue-400 bg-blue-500/5' : 'border-slate-600 hover:border-slate-500 bg-slate-800/50'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              multiple 
              accept=".csv,.json" 
              className="hidden" 
              ref={fileInputRef} 
              onChange={handleFileChange}
            />
            <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <p className="text-lg font-medium text-slate-200">Drop CSE data files here</p>
            <p className="text-slate-400 text-sm mt-2">CSV or JSON files for alerts, cases, and asset inventory</p>
          </div>

          {files.length > 0 && (
            <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
              <h3 className="font-semibold mb-3 text-slate-200">Staged Files ({files.length})</h3>
              <ul className="space-y-2">
                {files.map((f, i) => (
                  <li key={i} className="flex items-center justify-between bg-slate-700/50 p-3 rounded text-sm">
                    <div className="flex items-center gap-3">
                      <FileType className="w-5 h-5 text-blue-400" />
                      <span className="font-medium">{f.name}</span>
                      <span className="text-slate-400 text-xs">{(f.size / 1024).toFixed(1)} KB</span>
                    </div>
                    <button onClick={() => removeFile(i)} className="text-slate-400 hover:text-red-400">
                      <XCircle className="w-5 h-5" />
                    </button>
                  </li>
                ))}
              </ul>
              
              <div className="mt-6 flex items-center justify-end gap-4">
                {uploading && (
                  <div className="flex-1 flex items-center gap-3">
                    <div className="w-full bg-slate-700 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${progress}%` }}></div>
                    </div>
                    <span className="text-sm text-slate-400 w-12">{progress}%</span>
                  </div>
                )}
                <button 
                  onClick={handleUpload} 
                  disabled={uploading}
                  className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
                >
                  {uploading ? 'Uploading...' : 'Upload Files'}
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <div className="flex items-center gap-3 mb-6">
            <CheckCircle className="w-8 h-8 text-green-500" />
            <div>
              <h2 className="text-2xl font-bold text-green-400">Upload Complete</h2>
              <p className="text-slate-400 text-sm font-mono mt-1">Batch ID: {summary.batch_id}</p>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="bg-slate-700/50 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">Alerts</p>
              <p className="text-2xl font-bold">{summary.records_parsed?.alerts || 0}</p>
            </div>
            <div className="bg-slate-700/50 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">Cases</p>
              <p className="text-2xl font-bold">{summary.records_parsed?.cases || 0}</p>
            </div>
            <div className="bg-slate-700/50 p-4 rounded-lg">
              <p className="text-slate-400 text-sm">Assets</p>
              <p className="text-2xl font-bold">{summary.records_parsed?.assets || 0}</p>
            </div>
          </div>

          <div className="flex justify-end">
            <button 
              onClick={handleRunAnalysis} 
              disabled={analysing}
              className="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-lg font-bold transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {analysing ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Analysing CSE submissions...
                </>
              ) : (
                'Run Analysis'
              )}
            </button>
          </div>
        </div>
      )}

      <div className="mt-12 bg-slate-800/50 rounded-xl p-5 border border-slate-700">
        <div className="flex items-center gap-2 mb-4">
          <Info className="w-5 h-5 text-blue-400" />
          <h3 className="font-semibold text-slate-200">Data Format Tips</h3>
        </div>
        <p className="text-sm text-slate-400 mb-2">Ensure your CSV/JSON files contain these key fields:</p>
        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="font-medium text-slate-300 block mb-1">Alerts</span>
            <ul className="list-disc list-inside text-slate-500">
              <li>alert_id</li>
              <li>cse_id</li>
              <li>category</li>
              <li>severity</li>
            </ul>
          </div>
          <div>
            <span className="font-medium text-slate-300 block mb-1">Cases</span>
            <ul className="list-disc list-inside text-slate-500">
              <li>case_id</li>
              <li>cse_id</li>
              <li>status</li>
              <li>resolution</li>
            </ul>
          </div>
          <div>
            <span className="font-medium text-slate-300 block mb-1">Assets</span>
            <ul className="list-disc list-inside text-slate-500">
              <li>asset_id</li>
              <li>cse_id</li>
              <li>criticality</li>
              <li>os_type</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
