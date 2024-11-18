import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const Card = ({ children, className = "" }) => (
  <div className={`rounded-lg border bg-white shadow-sm ${className}`}>
    {children}
  </div>
);

const EmptyState = () => (
  <div className="text-center py-12">
    <h3 className="text-lg font-medium text-gray-900 mb-2">No Screenshots Yet</h3>
    <p className="text-gray-500 mb-4">
      Press Win + Shift + S to capture a screenshot. 
      The analysis will appear here automatically.
    </p>
    <div className="bg-gray-50 p-4 rounded-lg max-w-md mx-auto">
      <ol className="list-decimal text-left pl-5 space-y-2 text-sm text-gray-600">
        <li>Press Win + Shift + S to start capturing</li>
        <li>Select the area you want to capture</li>
        <li>Wait for the analysis to complete</li>
        <li>Results will appear here automatically</li>
      </ol>
    </div>
  </div>
);

const MarkdownRenderer = ({ content }) => (
  <div className="markdown-content prose prose-slate max-w-none">
    <ReactMarkdown 
      remarkPlugins={[remarkGfm]}
      components={{
        // ... (keep other component styles)
        code: ({node, inline, className, children, ...props}) => {
          const match = /language-(\w+)/.exec(className || '');
          return inline ? (
            <code
              className="px-1.5 py-0.5 bg-gray-100 text-gray-900 rounded font-mono text-sm"
              {...props}
            >
              {children}
            </code>
          ) : (
            <div className="relative">
              {match && (
                <div className="absolute right-2 top-2 text-xs text-gray-400">
                  {match[1]}
                </div>
              )}
              <pre 
                className="!p-0 !m-0 !bg-transparent"
                style={{ background: 'transparent' }}
              >
                <code
                  className={`block bg-[#1e1e1e] text-[#d4d4d4] p-4 rounded-lg my-4 text-sm font-mono overflow-x-auto ${className}`}
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </code>
              </pre>
            </div>
          )
        },
        pre: ({node, ...props}) => (
          <pre 
            className="!p-0 !m-0 !bg-transparent" 
            style={{ background: 'transparent' }}
            {...props}
          />
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  </div>
);

const AnalysisViewer = () => {
  const [analyses, setAnalyses] = useState([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadAnalyses = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/analyses');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        const analysesArray = Object.entries(data)
          .map(([filename, analysis]) => ({
            filename,
            ...analysis
          }))
          .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        setAnalyses(analysesArray);
        
        if (!selectedAnalysis && analysesArray.length > 0) {
          setSelectedAnalysis(analysesArray[0]);
        }
        
        setError(null);
      } catch (error) {
        console.error('Error loading analyses:', error);
        setError('Failed to load analyses. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    loadAnalyses();
    const interval = setInterval(loadAnalyses, 5000);
    return () => clearInterval(interval);
  }, [selectedAnalysis]);

  if (loading && analyses.length === 0) {
    return (
      <div className="flex h-screen bg-gray-100 p-6 items-center justify-center">
        <Card className="p-6">
          <div className="text-center">
            <p className="text-gray-600">Loading analyses...</p>
          </div>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen bg-gray-100 p-6 items-center justify-center">
        <Card className="p-6">
          <div className="text-center">
            <p className="text-red-600">{error}</p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100 p-6">
      {/* Left side - Screenshots */}
      <div className="w-1/2 pr-4 overflow-y-auto">
        <Card>
          <div className="p-6">
            <h3 className="text-2xl font-semibold mb-4">Screenshots</h3>
            {analyses.length === 0 ? (
              <EmptyState />
            ) : (
              <div className="grid grid-cols-2 gap-4">
                {analyses.map((analysis) => (
                  <div
                    key={analysis.filename}
                    className={`cursor-pointer rounded-lg border-2 p-2 transition-all duration-200 ${
                      selectedAnalysis?.filename === analysis.filename
                        ? 'border-blue-500 shadow-lg'
                        : 'border-transparent hover:border-gray-200 hover:shadow-md'
                    }`}
                    onClick={() => setSelectedAnalysis(analysis)}
                  >
                    <img
                      src={`/screenshots/${analysis.filename}`}
                      alt={analysis.filename}
                      className="w-full h-auto rounded"
                      onError={(e) => {
                        console.error('Image load error:', e);
                        e.target.src = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2VlZSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjE0Ij5JbWFnZSBub3QgZm91bmQ8L3RleHQ+PC9zdmc+';
                      }}
                    />
                    <p className="mt-2 text-sm text-gray-600">
                      {new Date(analysis.timestamp).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Right side - Analysis */}
      <div className="w-1/2 pl-4">
        <Card>
          <div className="p-6">
            <h3 className="text-2xl font-semibold mb-4">Analysis Result</h3>
            {!selectedAnalysis ? (
              <p className="text-gray-500">Select a screenshot to view its analysis</p>
            ) : (
              <div className="overflow-auto max-h-[calc(100vh-12rem)]">
                <MarkdownRenderer content={selectedAnalysis.final_solution || 'No analysis available'} />
                {loading && (
                  <div className="text-sm text-gray-500 mt-2">
                    Refreshing analysis...
                  </div>
                )}
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default AnalysisViewer;