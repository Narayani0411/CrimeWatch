import React, { useState } from "react";
import WebcamFeed from "../components/WebcamFeed";
import { Eye, EyeOff } from "lucide-react";

const DashboardPage = () => {
  const [isStreaming, setIsStreaming] = useState(false);

  return (
    <div className="fade-in flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-6">Dashboard 👁️</h1>

      <button
        onClick={() => setIsStreaming(!isStreaming)}
        className="btn text-white px-8 py-3 shadow-md"
      >
        {isStreaming ? "🛑 Stop Video" : "▶️ Start Video"}
      </button>

      <p className="mt-4 text-sm opacity-70">
        {isStreaming ? "Streaming is active." : "Video is currently stopped."}
      </p>

      <div className="card mt-8 w-full max-w-3xl">
        <WebcamFeed isStreaming={isStreaming} />
      </div>
    </div>
  );
};

export default DashboardPage;
