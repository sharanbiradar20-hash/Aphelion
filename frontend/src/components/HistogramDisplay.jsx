import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const HistogramDisplay = ({ histogramData, title = "Histogram" }) => {
  const [showOriginal, setShowOriginal] = useState(true);
  
  if (!histogramData || (!histogramData.original && !histogramData.processed)) {
    return null;
  }

  // Use the appropriate histogram data
  const activeHistogram = showOriginal ? histogramData.original : histogramData.processed;
  
  if (!activeHistogram || !Array.isArray(activeHistogram)) {
    return null;
  }

  // Transform histogram array to chart data
  const chartData = activeHistogram.map((frequency, intensity) => ({
    intensity: intensity,
    frequency: frequency
  }));

  // Sample data if histogram is too large for performance
  const sampledData = chartData.length > 256 ? 
    chartData.filter((_, index) => index % Math.ceil(chartData.length / 256) === 0) :
    chartData;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-800 p-3 border border-cyan-500/30 rounded-lg shadow-xl">
          <p className="font-medium text-cyan-300 text-sm">
            Intensity: {label}
          </p>
          <p className="text-blue-400 text-sm">
            Frequency: {payload[0].value.toLocaleString()}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl shadow-2xl p-6 backdrop-blur-sm bg-opacity-90 border border-cyan-500/20 transition-all duration-300 hover:shadow-cyan-500/20">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">{title}</h2>
        
        {/* Original/Processed Toggle */}
        <div className="flex gap-2">
          <button
            onClick={() => setShowOriginal(true)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              showOriginal
                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg'
                : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
            }`}
          >
            Original
          </button>
          <button
            onClick={() => setShowOriginal(false)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              !showOriginal
                ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg'
                : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
            }`}
          >
            Processed
          </button>
        </div>
      </div>

      {/* Histogram Chart */}
      <div className="bg-slate-900/50 rounded-xl p-4 border border-cyan-500/20">
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={sampledData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis 
              dataKey="intensity" 
              stroke="#94a3b8"
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              label={{ value: 'Intensity', position: 'insideBottom', offset: -5, fill: '#06b6d4' }}
            />
            <YAxis 
              stroke="#94a3b8"
              tick={{ fill: '#94a3b8', fontSize: 11 }}
              label={{ value: 'Frequency', angle: -90, position: 'insideLeft', fill: '#06b6d4' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar 
              dataKey="frequency" 
              fill="url(#colorGradient)" 
              radius={[4, 4, 0, 0]}
            />
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.8} />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.6} />
              </linearGradient>
            </defs>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Statistics */}
      <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div className="p-3 bg-slate-900/50 rounded-lg border border-cyan-500/20">
          <p className="text-slate-400 text-xs mb-1">Total Pixels</p>
          <p className="text-cyan-300 font-medium">{activeHistogram.reduce((a, b) => a + b, 0).toLocaleString()}</p>
        </div>
        <div className="p-3 bg-slate-900/50 rounded-lg border border-cyan-500/20">
          <p className="text-slate-400 text-xs mb-1">Intensity Range</p>
          <p className="text-cyan-300 font-medium">0 - {activeHistogram.length - 1}</p>
        </div>
      </div>
    </div>
  );
};

export default HistogramDisplay;

