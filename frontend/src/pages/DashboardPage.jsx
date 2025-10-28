import React, { useState } from 'react';
import WebcamFeed from '../components/WebcamFeed';

const DashboardPage = () => {
  const [isStreaming, setIsStreaming] = useState(false); // Start as false by default

  const toggleStream = () => {
    setIsStreaming(!isStreaming);
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Dashboard 👁️</h1>

      {/* Control Buttons */}
      <div className="mb-6">
        <button
          onClick={toggleStream}
          className={`py-2 px-6 rounded-lg font-semibold transition duration-200 ${
            isStreaming
              ? 'bg-red-600 hover:bg-red-700 text-white shadow-lg'
              : 'bg-green-600 hover:bg-green-700 text-white shadow-lg'
          }`}
        >
          {isStreaming ? '🛑 Stop Video' : '▶️ Start Video'}
        </button>
        <p className="mt-2 text-sm text-gray-500">
            {isStreaming ? 'Streaming is active.' : 'Video is currently stopped.'}
        </p>
      </div>

      <WebcamFeed isStreaming={isStreaming} />

    </div>
  );
};

export default DashboardPage;