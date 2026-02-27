import React from 'react';

const FilterControls = ({
  modules,
  selectedModule,
  setSelectedModule,
  selectedOperation,
  setSelectedOperation,
  processingParams,
  setProcessingParams,
  onProcessing,
  isProcessing,
  hasImage
}) => {
  const handleModuleChange = (moduleId) => {
    setSelectedModule(moduleId);
    setSelectedOperation('');
    setProcessingParams({});
  };

  const handleOperationChange = (operationId) => {
    setSelectedOperation(operationId);
    setProcessingParams({});
  };

  const handleParamChange = (paramName, value) => {
    setProcessingParams(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const handleProcess = () => {
    if (!selectedOperation) {
      alert('Please select an operation');
      return;
    }
    onProcessing(selectedOperation, processingParams);
  };

  const getOperationParams = (operationId) => {
    const params = {
      // Intensity operations
      linear_transform: [
        { name: 'alpha', label: 'Alpha (slope)', type: 'number', default: 1.0, min: 0, max: 5, step: 0.1 },
        { name: 'beta', label: 'Beta (offset)', type: 'number', default: 0, min: -255, max: 255, step: 1 }
      ],
      power_transform: [
        { name: 'gamma', label: 'Gamma', type: 'number', default: 1.0, min: 0.1, max: 3.0, step: 0.1 },
        { name: 'c', label: 'Constant (c)', type: 'number', default: 1.0, min: 0.1, max: 10.0, step: 0.1 }
      ],
      gamma_correction: [
        { name: 'gamma', label: 'Gamma', type: 'number', default: 1.0, min: 0.1, max: 3.0, step: 0.1 }
      ],
      contrast_stretching: [
        { name: 'min_val', label: 'Min Value', type: 'number', default: 0, min: 0, max: 255, step: 1 },
        { name: 'max_val', label: 'Max Value', type: 'number', default: 255, min: 0, max: 255, step: 1 }
      ],
      // Frequency operations
      low_pass_filter: [
        { name: 'cutoff', label: 'Cutoff Frequency', type: 'number', default: 30, min: 1, max: 100, step: 1 },
        { name: 'filter_type', label: 'Filter Type', type: 'select', options: ['ideal', 'butterworth', 'gaussian'], default: 'butterworth' }
      ],
      high_pass_filter: [
        { name: 'cutoff', label: 'Cutoff Frequency', type: 'number', default: 30, min: 1, max: 100, step: 1 },
        { name: 'filter_type', label: 'Filter Type', type: 'select', options: ['ideal', 'butterworth', 'gaussian'], default: 'butterworth' }
      ],
      // Restoration operations
      add_noise: [
        { name: 'noise_type', label: 'Noise Type', type: 'select', options: ['gaussian', 'salt_pepper', 'uniform'], default: 'gaussian' },
        { name: 'noise_level', label: 'Noise Level', type: 'number', default: 10, min: 1, max: 100, step: 1 }
      ],
      // Color operations
      color_space_conversion: [
        { name: 'target_space', label: 'Target Color Space', type: 'select', options: ['hsv', 'lab', 'ycbcr', 'xyz'], default: 'hsv' }
      ]
    };
    return params[operationId] || [];
  };

  const renderParamInput = (param) => {
    const value = processingParams[param.name] || param.default;

    switch (param.type) {
      case 'number':
        return (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <input
                type="range"
                min={param.min}
                max={param.max}
                step={param.step}
                value={value}
                onChange={(e) => handleParamChange(param.name, parseFloat(e.target.value))}
                className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer slider-cyan"
              />
              <input
                type="number"
                min={param.min}
                max={param.max}
                step={param.step}
                value={value}
                onChange={(e) => handleParamChange(param.name, parseFloat(e.target.value))}
                className="ml-3 w-20 px-2 py-1 bg-slate-700 border border-cyan-500/30 rounded-md text-cyan-300 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
              />
            </div>
          </div>
        );
      case 'select':
        return (
          <select
            value={value}
            onChange={(e) => handleParamChange(param.name, e.target.value)}
            className="w-full px-3 py-2 bg-slate-700 border border-cyan-500/30 rounded-md text-cyan-300 focus:outline-none focus:ring-2 focus:ring-cyan-500 cursor-pointer"
          >
            {param.options.map(option => (
              <option key={option} value={option} className="bg-slate-800">
                {option.charAt(0).toUpperCase() + option.slice(1)}
              </option>
            ))}
          </select>
        );
      default:
        return (
          <input
            type="text"
            value={value}
            onChange={(e) => handleParamChange(param.name, e.target.value)}
            className="w-full px-3 py-2 bg-slate-700 border border-cyan-500/30 rounded-md text-cyan-300 focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
        );
    }
  };

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl shadow-2xl p-6 backdrop-blur-sm bg-opacity-90 border border-cyan-500/20 transition-all duration-300 hover:shadow-cyan-500/20">
      <h2 className="text-2xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Processing Controls</h2>
      
      {/* Module Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-cyan-300 mb-2">
          Processing Module
        </label>
        <select
          value={selectedModule}
          onChange={(e) => handleModuleChange(e.target.value)}
          className="w-full px-3 py-2 bg-slate-700 border border-cyan-500/30 rounded-md text-cyan-300 focus:outline-none focus:ring-2 focus:ring-cyan-500 cursor-pointer"
        >
          {Object.entries(modules).map(([id, module]) => (
            <option key={id} value={id} className="bg-slate-800">
              {module.name}
            </option>
          ))}
        </select>
      </div>

      {/* Operation Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-cyan-300 mb-2">
          Operation
        </label>
        <select
          value={selectedOperation}
          onChange={(e) => handleOperationChange(e.target.value)}
          className="w-full px-3 py-2 bg-slate-700 border border-cyan-500/30 rounded-md text-cyan-300 focus:outline-none focus:ring-2 focus:ring-cyan-500 cursor-pointer"
        >
          <option value="" className="bg-slate-800">Select an operation...</option>
          {modules[selectedModule]?.operations.map(operation => (
            <option key={operation.id} value={operation.id} className="bg-slate-800">
              {operation.name}
            </option>
          ))}
        </select>
      </div>

      {/* Operation Parameters */}
      {selectedOperation && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-cyan-300 mb-3">
            Parameters
          </label>
          <div className="space-y-4 p-4 bg-slate-800/50 rounded-lg border border-cyan-500/10">
            {getOperationParams(selectedOperation).map(param => (
              <div key={param.name}>
                <label className="block text-sm text-slate-300 mb-2">
                  {param.label}
                </label>
                {renderParamInput(param)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Process Button */}
      <button
        onClick={handleProcess}
        disabled={!hasImage || !selectedOperation || isProcessing}
        className={`w-full py-3 px-4 rounded-lg font-semibold transition-all duration-300 ${
          !hasImage || !selectedOperation || isProcessing
            ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
            : 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:from-cyan-600 hover:to-blue-600 shadow-lg hover:shadow-cyan-500/50 transform hover:scale-105'
        }`}
      >
        {isProcessing ? (
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-t-2 border-white mr-2"></div>
            Processing...
          </div>
        ) : (
          'Apply Filter'
        )}
      </button>

      {/* Module Description */}
      {selectedModule && (
        <div className="mt-6 p-4 bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg border border-cyan-500/20">
          <h3 className="font-semibold text-cyan-300 mb-2">
            {modules[selectedModule].name}
          </h3>
          <p className="text-sm text-slate-300">
            {getModuleDescription(selectedModule)}
          </p>
        </div>
      )}

      <style jsx>{`
        .slider-cyan::-webkit-slider-thumb {
          appearance: none;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: linear-gradient(135deg, #06b6d4, #3b82f6);
          cursor: pointer;
          border: 2px solid #0e7490;
          box-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
        }

        .slider-cyan::-moz-range-thumb {
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: linear-gradient(135deg, #06b6d4, #3b82f6);
          cursor: pointer;
          border: 2px solid #0e7490;
          box-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
        }
      `}</style>
    </div>
  );
};

const getModuleDescription = (moduleId) => {
  const descriptions = {
    fundamentals: 'Basic image operations including I/O, transformations, and statistics.',
    intensity: 'Intensity transformations and spatial filtering operations.',
    frequency: 'Frequency domain filtering and Fourier Transform operations.',
    restoration: 'Image restoration, noise reduction, and reconstruction techniques.',
    color: 'Color space conversions and color image processing operations.'
  };
  return descriptions[moduleId] || '';
};

export default FilterControls;

