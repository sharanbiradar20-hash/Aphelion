import React from 'react';

const MetricsPanel = ({ metrics, title = "Array Metrics" }) => {
  if (!metrics) {
    return null;
  }

  const renderMetricValue = (value) => {
    if (typeof value === 'number') {
      return value.toFixed(2);
    }
    return value;
  };

  const getMetricColor = (metricName, value) => {
    if (metricName === 'psnr' && typeof value === 'number') {
      if (value > 30) return 'text-green-400';
      if (value >= 20) return 'text-yellow-400';
      return 'text-red-400';
    }
    if (metricName === 'ssim' && typeof value === 'number') {
      if (value > 0.9) return 'text-green-400';
      if (value >= 0.7) return 'text-yellow-400';
      return 'text-red-400';
    }
    return 'text-cyan-300';
  };

  const getMetricBgColor = (metricName, value) => {
    if (metricName === 'psnr' && typeof value === 'number') {
      if (value > 30) return 'from-green-900/30 to-green-800/20 border-green-500/30';
      if (value >= 20) return 'from-yellow-900/30 to-yellow-800/20 border-yellow-500/30';
      return 'from-red-900/30 to-red-800/20 border-red-500/30';
    }
    if (metricName === 'ssim' && typeof value === 'number') {
      if (value > 0.9) return 'from-green-900/30 to-green-800/20 border-green-500/30';
      if (value >= 0.7) return 'from-yellow-900/30 to-yellow-800/20 border-yellow-500/30';
      return 'from-red-900/30 to-red-800/20 border-red-500/30';
    }
    return 'from-slate-800 to-slate-700 border-cyan-500/20';
  };

  const renderMetricSection = (sectionTitle, data, className = '') => {
    if (!data || typeof data !== 'object') {
      return null;
    }

    return (
      <div className={`p-4 rounded-lg bg-gradient-to-br ${className}`}>
        <h3 className="font-semibold mb-3 text-cyan-300">{sectionTitle}</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {Object.entries(data).map(([key, value]) => (
            <div key={key} className="flex justify-between items-center">
              <span className="text-sm text-slate-400 capitalize">
                {key.replace(/_/g, ' ')}:
              </span>
              <span className="text-sm font-semibold text-white">
                {renderMetricValue(value)}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl shadow-2xl p-6 backdrop-blur-sm bg-opacity-90 border border-cyan-500/20 transition-all duration-300 hover:shadow-cyan-500/20">
      <h2 className="text-2xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">{title}</h2>
      
      <div className="space-y-4">
        {/* Dimensions */}
        {renderMetricSection(
          'Image Dimensions',
          metrics.dimensions,
          'from-slate-800 to-slate-700 border border-cyan-500/20'
        )}

        {/* Intensity Statistics */}
        {renderMetricSection(
          'Intensity Statistics',
          metrics.intensity_statistics,
          'from-slate-800 to-slate-700 border border-cyan-500/20'
        )}

        {/* Image Quality */}
        {renderMetricSection(
          'Image Quality',
          metrics.image_quality,
          'from-slate-800 to-slate-700 border border-cyan-500/20'
        )}

        {/* Additional Metrics */}
        {metrics.psnr && (
          <div className="p-4 bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg border border-cyan-500/20">
            <h3 className="font-semibold mb-3 text-cyan-300">Quality Metrics</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className={`p-3 rounded-lg bg-gradient-to-br ${getMetricBgColor('psnr', metrics.psnr)} border group relative`}>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-400">PSNR:</span>
                  <span className={`text-lg font-bold ${getMetricColor('psnr', metrics.psnr)}`}>
                    {renderMetricValue(metrics.psnr)} dB
                  </span>
                </div>
                <div className="absolute hidden group-hover:block bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-slate-900 text-xs text-slate-300 rounded-lg shadow-xl border border-cyan-500/30 whitespace-nowrap z-10">
                  {metrics.psnr > 30 ? 'Excellent quality (>30dB)' : metrics.psnr >= 20 ? 'Good quality (20-30dB)' : 'Poor quality (<20dB)'}
                </div>
              </div>
              {metrics.ssim && (
                <div className={`p-3 rounded-lg bg-gradient-to-br ${getMetricBgColor('ssim', metrics.ssim)} border group relative`}>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-400">SSIM:</span>
                    <span className={`text-lg font-bold ${getMetricColor('ssim', metrics.ssim)}`}>
                      {renderMetricValue(metrics.ssim)}
                    </span>
                  </div>
                  <div className="absolute hidden group-hover:block bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-slate-900 text-xs text-slate-300 rounded-lg shadow-xl border border-cyan-500/30 whitespace-nowrap z-10">
                    {metrics.ssim > 0.9 ? 'Excellent similarity (>0.9)' : metrics.ssim >= 0.7 ? 'Good similarity (0.7-0.9)' : 'Poor similarity (<0.7)'}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Histogram Features */}
        {metrics.histogram_features && (
          <div className="p-4 bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg border border-cyan-500/20">
            <h3 className="font-semibold mb-3 text-cyan-300">Histogram Features</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Mean Intensity:</span>
                <span className="text-sm font-semibold text-white">
                  {renderMetricValue(metrics.histogram_features.mean_intensity)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Variance:</span>
                <span className="text-sm font-semibold text-white">
                  {renderMetricValue(metrics.histogram_features.variance)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Skewness:</span>
                <span className="text-sm font-semibold text-white">
                  {renderMetricValue(metrics.histogram_features.skewness)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Kurtosis:</span>
                <span className="text-sm font-semibold text-white">
                  {renderMetricValue(metrics.histogram_features.kurtosis)}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Texture Features */}
        {metrics.texture_features && (
          <div className="p-4 bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg border border-cyan-500/20">
            <h3 className="font-semibold mb-3 text-cyan-300">Texture Features</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Texture Mean:</span>
                <span className="text-sm font-semibold text-white">
                  {renderMetricValue(metrics.texture_features.texture_mean)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Texture Std:</span>
                <span className="text-sm font-semibold text-white">
                  {renderMetricValue(metrics.texture_features.texture_std)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Texture Variance:</span>
                <span className="text-sm font-semibold text-white">
                  {renderMetricValue(metrics.texture_features.texture_variance)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-400">Edge Density:</span>
                <span className="text-sm font-semibold text-white">
                  {renderMetricValue(metrics.texture_features.edge_density)}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Metrics Explanation */}
      <div className="mt-6 p-4 bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg border border-cyan-500/20">
        <h3 className="font-semibold text-cyan-300 mb-3 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          Metrics Explanation
        </h3>
        <div className="text-sm text-slate-300 space-y-2">
          <p><strong className="text-cyan-400">PSNR:</strong> Peak Signal-to-Noise Ratio - measures image quality (higher is better)</p>
          <p><strong className="text-cyan-400">SSIM:</strong> Structural Similarity Index - measures structural similarity (closer to 1 is better)</p>
        </div>
      </div>
    </div>
  );
};

export default MetricsPanel;

