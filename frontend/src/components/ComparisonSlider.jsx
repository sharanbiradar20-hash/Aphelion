import React, { useState, useRef, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Download, Columns, GalleryHorizontalEnd } from 'lucide-react';

// ─── Animated Processing Steps ──────────────────────────────
const PROCESSING_STEPS = [
  { label: 'Analyzing image', icon: '🔍', duration: 800 },
  { label: 'Applying transformation', icon: '⚙️', duration: 1200 },
  { label: 'Rendering result', icon: '🎨', duration: 600 },
];

const ProcessingOverlay = ({ isProcessing }) => {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    if (!isProcessing) {
      setActiveStep(0);
      return;
    }

    let stepIndex = 0;
    const advanceStep = () => {
      stepIndex = Math.min(stepIndex + 1, PROCESSING_STEPS.length - 1);
      setActiveStep(stepIndex);
    };

    const timers = PROCESSING_STEPS.slice(0, -1).map((step, i) => {
      const delay = PROCESSING_STEPS.slice(0, i + 1).reduce((s, st) => s + st.duration, 0);
      return setTimeout(advanceStep, delay);
    });

    return () => timers.forEach(clearTimeout);
  }, [isProcessing]);

  if (!isProcessing) return null;

  return (
    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center rounded-xl z-20">
      <motion.div
        className="bg-gradient-to-br from-slate-800 to-slate-900 p-8 rounded-2xl shadow-2xl border border-cyan-500/30 min-w-[320px]"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.25 }}
      >
        {/* Step indicators */}
        <div className="space-y-4">
          {PROCESSING_STEPS.map((step, i) => {
            const isActive = i === activeStep;
            const isComplete = i < activeStep;

            return (
              <motion.div
                key={step.label}
                className="flex items-center gap-3"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
              >
                {/* Step circle */}
                <div className={`relative flex items-center justify-center w-8 h-8 rounded-full border-2 transition-all duration-300 ${isComplete
                  ? 'bg-cyan-500 border-cyan-500'
                  : isActive
                    ? 'border-cyan-400 bg-cyan-500/20'
                    : 'border-slate-600 bg-slate-800'
                  }`}>
                  {isComplete ? (
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : isActive ? (
                    <div className="w-3 h-3 rounded-full bg-cyan-400 animate-pulse"></div>
                  ) : (
                    <span className="text-xs text-slate-500">{i + 1}</span>
                  )}

                  {/* Connecting line */}
                  {i < PROCESSING_STEPS.length - 1 && (
                    <div className={`absolute top-full left-1/2 -translate-x-1/2 w-0.5 h-4 transition-colors duration-300 ${isComplete ? 'bg-cyan-500' : 'bg-slate-700'
                      }`} />
                  )}
                </div>

                {/* Step label */}
                <div className="flex-1">
                  <span className={`text-sm font-medium transition-colors duration-300 ${isActive ? 'text-cyan-300' : isComplete ? 'text-slate-400' : 'text-slate-500'
                    }`}>
                    {step.icon} {step.label}
                    {isActive && (
                      <motion.span
                        className="inline-block ml-1"
                        animate={{ opacity: [1, 0.3, 1] }}
                        transition={{ repeat: Infinity, duration: 1 }}
                      >...</motion.span>
                    )}
                  </span>
                </div>

                {/* Status indicator */}
                {isComplete && (
                  <motion.span
                    className="text-xs text-cyan-400 font-mono"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >Done</motion.span>
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Progress bar */}
        <div className="mt-6 h-1.5 bg-slate-700 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
            initial={{ width: '5%' }}
            animate={{ width: `${((activeStep + 1) / PROCESSING_STEPS.length) * 100}%` }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
          />
        </div>
      </motion.div>
    </div>
  );
};

// ─── Main Component ─────────────────────────────────────────
const ComparisonSlider = ({ originalImage, processedImage, isProcessing }) => {
  const containerRef = useRef(null);
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const [viewMode, setViewMode] = useState('slider'); // 'slider' | 'sideBySide'

  const updateSliderPosition = useCallback((clientX) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
    setSliderPosition(percentage);
  }, []);

  const handleMouseDown = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
    updateSliderPosition(e.clientX);
  }, [updateSliderPosition]);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging) return;
    updateSliderPosition(e.clientX);
  }, [isDragging, updateSliderPosition]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleTouchStart = useCallback((e) => {
    setIsDragging(true);
    updateSliderPosition(e.touches[0].clientX);
  }, [updateSliderPosition]);

  const handleTouchMove = useCallback((e) => {
    if (!isDragging) return;
    updateSliderPosition(e.touches[0].clientX);
  }, [isDragging, updateSliderPosition]);

  // Download helper
  const handleDownload = useCallback(async (dataUrl, filename) => {
    try {
      const res = await fetch(dataUrl);
      const blob = await res.blob();
      const blobUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(blobUrl);
    } catch (err) {
      console.error('Download failed:', err);
    }
  }, []);

  // Global mouse/touch listeners
  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      window.addEventListener('touchmove', handleTouchMove);
      window.addEventListener('touchend', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('touchmove', handleTouchMove);
      window.removeEventListener('touchend', handleMouseUp);
    };
  }, [isDragging, handleMouseMove, handleMouseUp, handleTouchMove]);

  if (!originalImage) return null;

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl shadow-2xl p-6 backdrop-blur-sm bg-opacity-90 border border-cyan-500/20 transition-all duration-300 hover:shadow-cyan-500/20 card-glow">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
          Image Comparison
        </h2>

        <div className="flex items-center gap-2">
          {/* View mode toggle */}
          <div className="flex items-center bg-slate-800 rounded-lg border border-slate-700 p-0.5">
            <button
              onClick={() => setViewMode('slider')}
              className={`flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium rounded-md transition-all duration-200 ${viewMode === 'slider'
                ? 'bg-cyan-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
                }`}
              title="Slider mode"
            >
              <GalleryHorizontalEnd className="w-3.5 h-3.5" />
              Slider
            </button>
            <button
              onClick={() => setViewMode('sideBySide')}
              className={`flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium rounded-md transition-all duration-200 ${viewMode === 'sideBySide'
                ? 'bg-cyan-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
                }`}
              title="Side by side"
            >
              <Columns className="w-3.5 h-3.5" />
              Side by Side
            </button>
          </div>

          {/* Divider */}
          <div className="w-px h-6 bg-slate-700"></div>

          {/* Download buttons */}
          <button
            onClick={() => handleDownload(originalImage, 'original-image.png')}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-800 border border-slate-700 rounded-lg hover:border-cyan-500/40 hover:text-cyan-300 transition-all duration-200"
            title="Download original image"
          >
            <Download className="w-3.5 h-3.5" />
            Original
          </button>
          {processedImage && (
            <button
              onClick={() => handleDownload(processedImage, 'processed-image.png')}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-gradient-to-r from-cyan-600 to-blue-600 rounded-lg hover:from-cyan-500 hover:to-blue-500 shadow-lg shadow-cyan-500/20 transition-all duration-200"
              title="Download processed image"
            >
              <Download className="w-3.5 h-3.5" />
              Processed
            </button>
          )}
        </div>
      </div>

      <div className="relative">
        <AnimatePresence mode="wait">
          {/* ─── SLIDER MODE ─── */}
          {viewMode === 'slider' && (
            <motion.div
              key="slider"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <div
                ref={containerRef}
                className="comparison-container"
                onMouseDown={handleMouseDown}
                onTouchStart={handleTouchStart}
              >
                <img src={originalImage} alt="Base" className="w-full h-auto object-contain opacity-0" />

                {/* Original (left) */}
                <div className="absolute inset-0">
                  <img
                    src={originalImage}
                    alt="Original"
                    className="w-full h-full object-contain"
                    style={{ clipPath: `polygon(0% 0%, ${sliderPosition}% 0%, ${sliderPosition}% 100%, 0% 100%)` }}
                    draggable={false}
                  />
                </div>

                {/* Processed (right) */}
                <div className="absolute inset-0">
                  <img
                    src={processedImage || originalImage}
                    alt="Processed"
                    className="w-full h-full object-contain"
                    style={{ clipPath: `polygon(${sliderPosition}% 0%, 100% 0%, 100% 100%, ${sliderPosition}% 100%)` }}
                    draggable={false}
                  />
                </div>

                {/* Handle */}
                <div className="comparison-handle" style={{ left: `${sliderPosition}%`, transform: 'translateX(-50%)' }}>
                  <motion.div className="comparison-handle-grip" whileHover={{ scale: 1.2 }} whileTap={{ scale: 0.95 }}>
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M15 19l-7-7 7-7M9 5l7 7-7 7" />
                    </svg>
                  </motion.div>
                </div>

                {/* Labels */}
                <div className="comparison-label comparison-label-original">Original</div>
                <div className="comparison-label comparison-label-processed">
                  {processedImage ? 'Processed' : 'Original'}
                </div>
              </div>

              {/* Slider position indicator */}
              <div className="mt-4 flex items-center justify-between text-xs">
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                  <span className="text-cyan-300 font-medium">Original</span>
                </div>
                <span className="text-slate-500 font-mono">{sliderPosition.toFixed(0)}%</span>
                <div className="flex items-center gap-1.5">
                  <span className="text-blue-300 font-medium">Processed</span>
                  <span className="w-2 h-2 rounded-full bg-blue-400"></span>
                </div>
              </div>
            </motion.div>
          )}

          {/* ─── SIDE BY SIDE MODE ─── */}
          {viewMode === 'sideBySide' && (
            <motion.div
              key="sideBySide"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <div className="grid grid-cols-2 gap-4">
                {/* Original */}
                <div className="relative group">
                  <div className="rounded-lg overflow-hidden border border-cyan-500/20 bg-black/20">
                    <img
                      src={originalImage}
                      alt="Original"
                      className="w-full h-auto object-contain"
                      draggable={false}
                    />
                  </div>
                  <div className="mt-2 flex items-center justify-center gap-1.5 text-xs">
                    <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                    <span className="text-cyan-300 font-medium">Original</span>
                  </div>
                </div>

                {/* Processed */}
                <div className="relative group">
                  <div className="rounded-lg overflow-hidden border border-blue-500/20 bg-black/20">
                    <img
                      src={processedImage || originalImage}
                      alt="Processed"
                      className="w-full h-auto object-contain"
                      draggable={false}
                    />
                  </div>
                  <div className="mt-2 flex items-center justify-center gap-1.5 text-xs">
                    <span className="w-2 h-2 rounded-full bg-blue-400"></span>
                    <span className="text-blue-300 font-medium">
                      {processedImage ? 'Processed' : 'Original'}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Animated Processing Overlay */}
        <ProcessingOverlay isProcessing={isProcessing} />
      </div>
    </div>
  );
};

export default ComparisonSlider;
