import React, { useState } from 'react';

const FrequencyVisualization = ({ frequencyData }) => {
  const [selectedView, setSelectedView] = useState('magnitude');
  const [zoomLevel, setZoomLevel] = useState(1);

  if (!frequencyData) {
    return null;
  }

  const views = [
    { id: 'magnitude', label: 'Magnitude Spectrum', image: frequencyData.magnitude_spectrum },
    { id: 'filtered', label: 'Filtered Spectrum', image: frequencyData.filtered_spectrum },
    { id: 'filter_mask', label: 'Filter Mask', image: frequencyData.filter_mask },
    { id: 'phase', label: 'Phase Spectrum', image: frequencyData.phase_spectrum }
  ];

  const handleZoomIn = () => {
    setZoomLevel(prev => Math.min(prev + 0.25, 3));
  };

  const handleZoomOut = () => {
    setZoomLevel(prev => Math.max(prev - 0.25, 1));
  };

  const handleZoomReset = () => {
    setZoomLevel(1);
  };

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl shadow-2xl p-6 backdrop-blur-sm bg-opacity-90 border border-cyan-500/20 transition-all duration-300 hover:shadow-cyan-500/20">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
          Frequency Domain Analysis
        </h2>
        
        {/* Zoom Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomOut}
            disabled={zoomLevel <= 1}
            className="p-2 bg-slate-700 text-cyan-300 rounded-lg hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            title="Zoom Out"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
            </svg>
          </button>
          <span className="text-cyan-300 text-sm font-medium min-w-[60px] text-center">
            {(zoomLevel * 100).toFixed(0)}%
          </span>
          <button
            onClick={handleZoomIn}
            disabled={zoomLevel >= 3}
            className="p-2 bg-slate-700 text-cyan-300 rounded-lg hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            title="Zoom In"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
            </svg>
          </button>
          <button
            onClick={handleZoomReset}
            className="p-2 bg-slate-700 text-cyan-300 rounded-lg hover:bg-slate-600 transition-all text-xs font-medium px-3"
            title="Reset Zoom"
          >
            Reset
          </button>
        </div>
      </div>

      {/* View Selector */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {views.map(view => (
          <button
            key={view.id}
            onClick={() => setSelectedView(view.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              selectedView === view.id
                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg shadow-cyan-500/30'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            {view.label}
          </button>
        ))}
      </div>

      {/* Single View Display */}
      <div className="bg-slate-900/50 rounded-lg p-4 border border-cyan-500/10 mb-6 overflow-auto">
        <div className="flex items-center justify-center min-h-[400px]">
          {views.find(v => v.id === selectedView)?.image ? (
            <img
              src={views.find(v => v.id === selectedView).image}
              alt={views.find(v => v.id === selectedView).label}
              className="max-w-full h-auto rounded-lg shadow-lg transition-transform duration-300"
              style={{ transform: `scale(${zoomLevel})` }}
            />
          ) : (
            <div className="text-slate-400 text-center">
              <svg className="w-16 h-16 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p>No {views.find(v => v.id === selectedView)?.label} available</p>
            </div>
          )}
        </div>
      </div>

      {/* 2x2 Grid View */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-cyan-300 mb-3">Complete Analysis Grid</h3>
        <div className="grid grid-cols-2 gap-4">
          {views.map(view => (
            <div
              key={view.id}
              className="bg-slate-900/50 rounded-lg p-3 border border-cyan-500/10 hover:border-cyan-500/30 transition-all cursor-pointer"
              onClick={() => setSelectedView(view.id)}
            >
              <h4 className="text-sm font-medium text-cyan-300 mb-2">{view.label}</h4>
              <div className="flex items-center justify-center bg-slate-800/50 rounded-lg min-h-[150px]">
                {view.image ? (
                  <img
                    src={view.image}
                    alt={view.label}
                    className="max-w-full h-auto rounded-lg"
                  />
                ) : (
                  <div className="text-slate-500 text-xs text-center">
                    <svg className="w-8 h-8 mx-auto mb-1 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Not available
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Information Panel */}
      <div className="p-4 bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg border border-cyan-500/20">
        <h3 className="font-semibold text-cyan-300 mb-2 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          Frequency Domain Information
        </h3>
        <div className="text-sm text-slate-300 space-y-2">
          <p>
            <strong className="text-cyan-400">Magnitude Spectrum:</strong> Shows the frequency content of the image. 
            Bright areas indicate high frequency components.
          </p>
          <p>
            <strong className="text-cyan-400">Filter Mask:</strong> Visualization of the frequency filter applied to the image.
          </p>
          <p>
            <strong className="text-cyan-400">Filtered Spectrum:</strong> Result of applying the filter mask to the magnitude spectrum.
          </p>
          <p>
            <strong className="text-cyan-400">Phase Spectrum:</strong> Contains phase information of the Fourier transform.
          </p>
        </div>
      </div>
    </div>
  );
};

export default FrequencyVisualization;
