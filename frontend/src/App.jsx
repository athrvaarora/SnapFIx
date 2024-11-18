import React from 'react';
import AnalysisViewer from './components/AnalysisViewer';

const App = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto py-4 px-6">
          <h1 className="text-2xl font-bold text-gray-900">SnapFix Analysis</h1>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 px-6">
        <AnalysisViewer />
      </main>
    </div>
  );
};

export default App;