import React, { useState, useCallback, useEffect, useRef } from 'react';
import './styles/App.css';
import axios from 'axios';
import FilterControls from './components/FilterControls';
import ComparisonSlider from './components/ComparisonSlider';
import HistogramDisplay from './components/HistogramDisplay';
import MetricsPanel from './components/MetricsPanel';
import { RotatingText } from './components/ui/rotating-text';
import TubesBackground from './components/ui/neon-flow';
import { InteractiveHoverButton } from './components/ui/interactive-hover-button';

// ─── Toast System ───────────────────────────────────────────
const Toast = ({ message, type, onClose }) => {
  const [exiting, setExiting] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setExiting(true);
      setTimeout(onClose, 300);
    }, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const icons = {
    success: (
      <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
      </svg>
    ),
    error: (
      <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
      </svg>
    ),
    info: (
      <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
      </svg>
    ),
  };

  return (
    <div className={`toast toast-${type} ${exiting ? 'toast-exit' : ''}`}>
      {icons[type]}
      <span className="flex-1">{message}</span>
      <button
        onClick={() => { setExiting(true); setTimeout(onClose, 300); }}
        className="ml-2 opacity-60 hover:opacity-100 transition-opacity"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};

// ─── Empty State Hero (with built-in upload) ────────────────
const EmptyStateHero = ({ onImageUpload }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const MAX_FILE_SIZE = 10 * 1024 * 1024;
  const ALLOWED_TYPES = ['image/png', 'image/jpeg', 'image/jpg', 'image/tiff', 'image/bmp'];

  const validateFile = (file) => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return 'Invalid file type. Please upload PNG, JPG, JPEG, TIFF, or BMP images.';
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File size exceeds 10MB limit. Your file is ${(file.size / 1024 / 1024).toFixed(2)}MB.`;
    }
    return null;
  };

  const handleFile = async (file) => {
    setError(null);
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('http://localhost:5000/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percent);
        },
      });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        onImageUpload(e.target.result, response.data);
      };
      reader.readAsDataURL(file);
    } catch (err) {
      console.error('Upload error:', err);
      setError('Upload failed: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) handleFile(e.target.files[0]);
  };

  return (
    <div
      className={`empty-state rounded-2xl p-12 flex flex-col items-center justify-center min-h-[500px] text-center transition-all duration-300 ${dragActive ? 'border-cyan-400 bg-cyan-500/10 scale-[1.01]' : ''
        }`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleChange}
        className="hidden"
        disabled={uploading}
      />

      {uploading ? (
        /* Upload in progress */
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-t-2 border-cyan-400 mb-4"></div>
          <p className="text-cyan-300 font-medium text-lg mb-4">Uploading image...</p>
          <div className="w-64">
            <div className="progress-bar-track">
              <div className="progress-bar-fill" style={{ width: `${uploadProgress}%` }}></div>
            </div>
            <p className="text-xs text-slate-500 mt-1.5 text-right font-mono">{uploadProgress}%</p>
          </div>
        </div>
      ) : (
        /* Default state */
        <>
          <div className="relative mb-8">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-cyan-500/10 to-blue-500/10 flex items-center justify-center border border-cyan-500/20">
              <svg className="w-12 h-12 text-cyan-400 header-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div className="absolute inset-0 orbit-ring" style={{ width: '140px', height: '140px', margin: '-22px' }}>
              <div className="w-3 h-3 rounded-full bg-cyan-400/60 absolute top-0 left-1/2 -translate-x-1/2 shadow-lg shadow-cyan-400/30"></div>
            </div>
          </div>

          <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mb-3">
            {dragActive ? 'Drop Image Here' : 'No Image Loaded'}
          </h3>
          <p className="text-slate-400 max-w-sm mb-8 leading-relaxed">
            {dragActive
              ? 'Release to upload your satellite or digital image.'
              : 'Drag and drop an image here, or click the button below. Supports PNG, JPG, TIFF, BMP up to 10MB.'}
          </p>

          <div
            className="cursor-pointer mb-8"
            onClick={() => fileInputRef.current?.click()}
          >
            <InteractiveHoverButton text="Upload Image" className="w-44" />
          </div>

          {/* Feature pills */}
          <div className="flex flex-wrap gap-2 justify-center">
            {['Intensity Transforms', 'Frequency Filtering', 'Image Restoration', 'Color Processing'].map((f) => (
              <span key={f} className="px-3 py-1.5 bg-slate-800/80 border border-cyan-500/15 rounded-full text-xs text-slate-400 font-medium">
                {f}
              </span>
            ))}
          </div>
        </>
      )}

      {/* Error message */}
      {error && (
        <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg max-w-sm">
          <p className="text-red-400 text-sm flex items-center">
            <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            {error}
          </p>
        </div>
      )}
    </div>
  );
};

// ─── Main App ───────────────────────────────────────────────
function App() {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [imageInfo, setImageInfo] = useState(null);
  const [histogramData, setHistogramData] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [selectedModule, setSelectedModule] = useState('intensity');
  const [selectedOperation, setSelectedOperation] = useState('');
  const [processingParams, setProcessingParams] = useState({});
  const [isProcessing, setIsProcessing] = useState(false);
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const handleImageUpload = (imageData, imageInfo) => {
    setUploadedImage(imageData);
    setImageInfo(imageInfo);
    setProcessedImage(null);
    setHistogramData(null);
    setMetrics(null);
    addToast('Image uploaded successfully!', 'success');
  };

  const handleProcessing = async (operation, params) => {
    if (!uploadedImage || !imageInfo || !imageInfo.file_id) {
      addToast('Please upload an image first.', 'error');
      return;
    }

    setIsProcessing(true);

    try {
      const moduleMap = {
        'intensity': 'module2',
        'frequency': 'module3',
        'restoration': 'module4',
        'color': 'module5'
      };

      const moduleEndpoint = moduleMap[selectedModule] || 'module2';

      const response = await fetch(`http://localhost:5000/api/process/${moduleEndpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_id: imageInfo.file_id,
          operation: operation,
          parameters: params
        })
      });

      const data = await response.json();

      if (data.success && data.processed_image) {
        const processedImageUrl = `data:image/png;base64,${data.processed_image}`;
        setProcessedImage(processedImageUrl);

        if (data.original_histogram && data.processed_histogram) {
          setHistogramData({
            original: data.original_histogram,
            processed: data.processed_histogram
          });
        }

        if (data.statistics) {
          setMetrics(data.statistics);
        }

        addToast('Processing completed successfully!', 'success');
      } else {
        throw new Error(data.error || 'Processing failed');
      }
    } catch (error) {
      console.error('Processing error:', error);
      addToast('Processing failed: ' + error.message, 'error');
    } finally {
      setIsProcessing(false);
    }
  };

  const modules = {
    intensity: {
      name: 'Intensity Transformations',
      operations: [
        { id: 'negative', name: 'Negative Transform' },
        { id: 'log', name: 'Log Transform' },
        { id: 'power_law', name: 'Power Law (Gamma)' },
        { id: 'histogram_eq', name: 'Histogram Equalization' },
        { id: 'smooth', name: 'Smoothing Filter' },
        { id: 'sharpen', name: 'Sharpening Filter' },
        { id: 'piecewise_linear', name: 'Piecewise Linear' }
      ]
    },
    frequency: {
      name: 'Frequency Domain',
      operations: [
        { id: 'compute_dft', name: 'Compute DFT' },
        { id: 'ideal_lp', name: 'Ideal Lowpass Filter' },
        { id: 'ideal_hp', name: 'Ideal Highpass Filter' },
        { id: 'butterworth_lp', name: 'Butterworth Lowpass' },
        { id: 'butterworth_hp', name: 'Butterworth Highpass' },
        { id: 'gaussian_lp', name: 'Gaussian Lowpass' },
        { id: 'gaussian_hp', name: 'Gaussian Highpass' }
      ]
    },
    restoration: {
      name: 'Image Restoration',
      operations: [
        { id: 'add_noise', name: 'Add Noise' },
        { id: 'inverse_filter', name: 'Inverse Filter' },
        { id: 'wiener_filter', name: 'Wiener Filter' },
        { id: 'cls_filter', name: 'Constrained Least Squares' },
        { id: 'periodic_noise_removal', name: 'Periodic Noise Removal' }
      ]
    },
    color: {
      name: 'Color Processing',
      operations: [
        { id: 'false_color', name: 'False Color Composite' },
        { id: 'rgb_enhance', name: 'RGB Enhancement' },
        { id: 'hsi_process', name: 'HSI Processing' },
        { id: 'pseudocolor', name: 'Pseudocolor' },
        { id: 'intensity_slicing', name: 'Intensity Slicing' },
      ]
    }
  };

  return (
    <TubesBackground className="min-h-screen" enableClickInteraction={true}>
      {/* ─── Toast Container ─── */}
      <div className="toast-container">
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>

      {/* ─── Header ─── */}
      <header className="app-header">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-center gap-3">
            {/* Satellite icon */}
            <div className="header-icon">
              <svg className="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
            </div>
            <div className="text-center">
              <h1 className="text-2xl md:text-3xl font-bold header-title tracking-tight">
                Aphelion
              </h1>
              <p className="text-xs md:text-sm text-slate-400 font-medium tracking-widest uppercase mt-0.5">
                <RotatingText
                  words={['Enhance', 'Restore', 'Transform', 'Analyze', 'Filter']}
                  mode="blur"
                  interval={2200}
                  className="text-cyan-400 font-semibold"
                />{' '}
                Satellite Imagery
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* ─── Main Content ─── */}
      <main className="container mx-auto px-4 py-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column — Controls */}
          <div className="lg:col-span-1 space-y-6">
            <div className="card-stagger">
              <FilterControls
                modules={modules}
                selectedModule={selectedModule}
                setSelectedModule={setSelectedModule}
                selectedOperation={selectedOperation}
                setSelectedOperation={setSelectedOperation}
                processingParams={processingParams}
                setProcessingParams={setProcessingParams}
                onProcessing={handleProcessing}
                isProcessing={isProcessing}
                hasImage={!!uploadedImage}
              />
            </div>

            {/* Change Image — only visible when an image is loaded */}
            {uploadedImage && (
              <div className="card-stagger">
                <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl p-5 border border-cyan-500/20 shadow-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-cyan-400 uppercase tracking-wider">Current Image</h3>
                  </div>
                  {imageInfo && (
                    <p className="text-xs text-slate-400 mb-3 truncate" title={imageInfo.filename}>
                      📁 {imageInfo.filename}
                    </p>
                  )}
                  <input
                    type="file"
                    accept="image/*"
                    id="change-image-input"
                    className="hidden"
                    onChange={async (e) => {
                      const file = e.target.files?.[0];
                      if (!file) return;
                      try {
                        const formData = new FormData();
                        formData.append('file', file);
                        const response = await axios.post('http://localhost:5000/api/upload', formData, {
                          headers: { 'Content-Type': 'multipart/form-data' },
                        });
                        if (response.data.error) throw new Error(response.data.error);
                        const reader = new FileReader();
                        reader.onload = (ev) => handleImageUpload(ev.target.result, response.data);
                        reader.readAsDataURL(file);
                      } catch (err) {
                        addToast('Upload failed: ' + err.message, 'error');
                      }
                      e.target.value = '';
                    }}
                  />
                  <label
                    htmlFor="change-image-input"
                    className="flex items-center justify-center gap-2 w-full py-2.5 px-4 text-sm font-medium text-white bg-gradient-to-r from-cyan-600 to-blue-600 rounded-lg hover:from-cyan-500 hover:to-blue-500 cursor-pointer transition-all duration-200 shadow-md shadow-cyan-500/20"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Change Image
                  </label>
                </div>
              </div>
            )}
          </div>

          {/* Right Column — Results */}
          <div className="lg:col-span-2 space-y-6">
            {uploadedImage ? (
              <>
                <div className="fade-in">
                  <ComparisonSlider
                    originalImage={uploadedImage}
                    processedImage={processedImage}
                    isProcessing={isProcessing}
                  />
                </div>

                {histogramData && (
                  <div className="fade-in">
                    <HistogramDisplay
                      histogramData={histogramData}
                      title="Image Histogram"
                    />
                  </div>
                )}

                {metrics && (
                  <div className="fade-in">
                    <MetricsPanel
                      metrics={metrics}
                      title="Image Metrics"
                    />
                  </div>
                )}
              </>
            ) : (
              <div className="card-stagger">
                <EmptyStateHero onImageUpload={handleImageUpload} />
              </div>
            )}
          </div>
        </div>
      </main>

      {/* ─── Footer ─── */}
      <footer className="relative z-10 mt-16 border-t border-slate-800/80">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse-glow"></div>
              <span className="text-sm text-slate-500 font-medium">
                Aphelion &copy; {new Date().getFullYear()}
              </span>
            </div>
            <p className="text-xs text-slate-600">
              Based on "Digital Image Processing" by Gonzalez &amp; Woods
            </p>
          </div>
        </div>
      </footer>
    </TubesBackground>
  );
}

export default App;
