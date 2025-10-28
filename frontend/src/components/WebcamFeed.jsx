import React, { useRef, useEffect, useState } from "react";

/**
 * Props:
 *  - isStreaming (boolean)
 *  - onAlert (function) => called with alert object returned from backend
 *  - captureIntervalMs (number) default 5000 (5s)
 */
const WebcamFeed = ({ isStreaming, onAlert, captureIntervalMs = 5000 }) => {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    const startStream = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        streamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch (err) {
        console.error("Error accessing webcam:", err);
        alert("Could not access webcam. Allow camera permissions.");
      }
    };

    const stopStream = () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }
      if (videoRef.current) videoRef.current.srcObject = null;
    };

    const sendFrameToServer = async () => {
      try {
        if (!videoRef.current) return;
        const video = videoRef.current;
        // prepare canvas
        const w = video.videoWidth || 640;
        const h = video.videoHeight || 480;
        const canvas = canvasRef.current || document.createElement("canvas");
        canvas.width = w;
        canvas.height = h;
        canvas.getContext("2d").drawImage(video, 0, 0, w, h);

        // convert to blob (jpeg to reduce size)
        canvas.toBlob(async (blob) => {
          if (!blob) return;
          const fd = new FormData();
          fd.append("frame", blob, `frame_${Date.now()}.jpg`);

          try {
            const res = await fetch("http://localhost:8000/upload-frame/", {
              method: "POST",
              body: fd,
            });
            if (!res.ok) {
              // non-fatal: just log
              console.warn("frame upload responded:", res.status);
              return;
            }
            const data = await res.json();
            // if backend signals an alert, call onAlert
            if (data?.alert) {
              onAlert && onAlert(data.alert);
            }
          } catch (e) {
            console.error("Error uploading frame:", e);
          }
        }, "image/jpeg", 0.8);
      } catch (e) {
        console.error("sendFrameToServer error:", e);
      }
    };

    if (isStreaming) {
      startStream();
      // start periodic capture once video has metadata
      const onLoaded = () => {
        // immediate first capture then periodic
        sendFrameToServer();
        intervalRef.current = setInterval(sendFrameToServer, captureIntervalMs);
      };
      videoRef.current && videoRef.current.addEventListener("loadedmetadata", onLoaded);

      // If metadata already loaded:
      if (videoRef.current && videoRef.current.readyState >= 1) {
        onLoaded();
      }

      return () => {
        videoRef.current && videoRef.current.removeEventListener("loadedmetadata", onLoaded);
        stopStream();
      };
    } else {
      stopStream();
    }

    // cleanup when component unmounts
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }
    };
  }, [isStreaming, captureIntervalMs, onAlert]);

  // invisible canvas used for capturing frames
  return (
    <div className="p-4 bg-gray-900 rounded-xl shadow-2xl">
      <h3 className="text-xl font-semibold mb-4 text-white">Live Webcam Feed</h3>
      {isStreaming ? (
        <>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full max-w-2xl border-4 border-red-500 rounded-lg"
          />
          <canvas ref={canvasRef} style={{ display: "none" }} />
        </>
      ) : (
        <div className="w-full max-w-2xl h-80 bg-gray-700 flex items-center justify-center rounded-lg">
          <p className="text-white text-lg">Video Feed Stopped</p>
        </div>
      )}
    </div>
  );
};

export default WebcamFeed;
