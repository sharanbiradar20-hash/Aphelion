import React from 'react';

const ProcessingPipeline = ({ originalImage, processedImage, intermediateResults, operationName }) => {
  if (!originalImage) {
    return null;
  }

  const hasIntermediateResults = intermediateResults && Object.keys(intermediateResults).length > 0;

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl shadow-2xl p-6 backdrop-blur-sm bg-opacity-90 border border-cyan-500/20 transition-all duration-300 hover:shadow-cyan-500/20">
      <h2 className="text-2xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
        Processing Pipeline
      </h2>

      {/* Pipeline Flow */}
      <div className="relative">
        {/* Main Pipeline */}
        <div className="flex items-center justify-between gap-4 mb-8">
          {/* Original Image */}
          <div className="flex-1">
            <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg p-4 border border-cyan-500/20">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-cyan-300 flex items-center">
                  <span className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold mr-2">
                    1
                  </span>
                  Original
                </h3>
                <span className="px-2 py-1 bg-cyan-500/20 text-cyan-300 text-xs rounded-full">
                  Input
                </span>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-2 border border-cyan-500/10">
                <img
                  src={originalImage}
                  alt="Original"
                  className="w-full h-auto rounded-lg"
                />
              </div>
            </div>
          </div>

          {/* Arrow */}
          <div className="flex flex-col items-center">
            <svg className="w-8 h-8 text-cyan-400 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </div>

          {/* Processing Module */}
          <div className="flex-1">
            <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 rounded-lg p-4 border border-blue-500/30">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-blue-300 flex items-center">
                  <span className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-xs font-bold mr-2">
                    2
                  </span>
                  Processing
                </h3>
                <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-full">
                  Module
                </span>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4 border border-blue-500/10 text-center">
                <svg className="w-12 h-12 mx-auto mb-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <p className="text-blue-300 text-xs font-medium">
                  {operationName || 'Processing...'}
                </p>
              </div>
            </div>
          </div>

          {/* Arrow */}
          <div className="flex flex-col items-center">
            <svg className="w-8 h-8 text-cyan-400 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </div>

          {/* Processed Image */}
          <div className="flex-1">
            <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg p-4 border border-green-500/30">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-green-300 flex items-center">
                  <span className="w-8 h-8 bg-gradient-to-br from-green-500 to-emerald-500 rounded-full flex items-center justify-center text-white text-xs font-bold mr-2">
                    3
                  </span>
                  Processed
                </h3>
                <span className="px-2 py-1 bg-green-500/20 text-green-300 text-xs rounded-full">
                  Output
                </span>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-2 border border-green-500/10">
                {processedImage ? (
                  <img
                    src={processedImage}
                    alt="Processed"
                    className="w-full h-auto rounded-lg"
                  />
                ) : (
                  <div className="flex items-center justify-center h-32 text-slate-500">
                    <div className="text-center">
                      <svg className="w-12 h-12 mx-auto mb-2 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <p className="text-xs">Awaiting processing</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Intermediate Results Section */}
        {hasIntermediateResults && (
          <div className="mt-8">
            <h3 className="text-lg font-semibold text-cyan-300 mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
              </svg>
              Intermediate Results
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {Object.entries(intermediateResults).map(([key, value], index) => (
                <div
                  key={key}
                  className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg p-3 border border-cyan-500/20 hover:border-cyan-500/40 transition-all"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-xs font-medium text-cyan-300 capitalize">
                      {key.replace(/_/g, ' ')}
                    </h4>
                    <span className="px-2 py-0.5 bg-cyan-500/20 text-cyan-400 text-xs rounded-full">
                      {index + 1}
                    </span>
                  </div>
                  <div className="bg-slate-900/50 rounded-lg p-2 border border-cyan-500/10">
                    {typeof value === 'string' && value.startsWith('data:image') ? (
                      <img
                        src={value}
                        alt={key}
                        className="w-full h-auto rounded-lg"
                      />
                    ) : (
                      <div className="text-slate-400 text-xs p-2">
                        {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pipeline Statistics */}
        <div className="mt-8 grid grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg p-4 border border-cyan-500/20 text-center">
            <div className="text-cyan-400 text-2xl font-bold mb-1">
              {hasIntermediateResults ? Object.keys(intermediateResults).length + 3 : 3}
            </div>
            <div className="text-slate-400 text-xs">Total Steps</div>
          </div>
          <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg p-4 border border-cyan-500/20 text-center">
            <div className="text-green-400 text-2xl font-bold mb-1">
              {processedImage ? '100%' : '0%'}
            </div>
            <div className="text-slate-400 text-xs">Completion</div>
          </div>
          <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg p-4 border border-cyan-500/20 text-center">
            <div className="text-blue-400 text-2xl font-bold mb-1">
              {operationName ? '1' : '0'}
            </div>
            <div className="text-slate-400 text-xs">Active Module</div>
          </div>
        </div>
      </div>

      {/* Information Panel */}
      <div className="mt-6 p-4 bg-gradient-to-br from-slate-800 to-slate-700 rounded-lg border border-cyan-500/20">
        <h3 className="font-semibold text-cyan-300 mb-2 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          Pipeline Information
        </h3>
        <div className="text-sm text-slate-300">
          <p>
            This visualization shows the complete image processing pipeline from input to output.
            {hasIntermediateResults && ' Intermediate results from frequency domain operations are displayed below.'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ProcessingPipeline;
