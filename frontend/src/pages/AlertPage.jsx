import React, { useEffect, useState } from "react";

const AlertItem = ({ alert }) => {
  return (
    <div className="p-4 bg-red-100 border-l-4 border-red-500 shadow-md flex justify-between items-start">
      <div className="w-full">
        <p className="font-semibold text-red-800">{alert.details || "Suspicious activity"}</p>
        <p className="text-sm text-gray-500">Timestamp: {alert.timestamp}</p>
        {alert.location && <p className="text-sm text-gray-600">Location: {alert.location}</p>}
        {alert.snapshot_url && (
          <div className="mt-2">
            <img src={alert.snapshot_url} alt="snapshot" className="max-w-xs rounded" />
          </div>
        )}
      </div>
    </div>
  );
};

const AlertPage = ({ initialAlerts = [] }) => {
  const [alerts, setAlerts] = useState(initialAlerts);

  // Fetch latest alerts from backend on mount
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("http://localhost:8000/alerts/");
        if (res.ok) {
          const data = await res.json();
          setAlerts(data.alerts || []);
        }
      } catch (e) {
        console.warn("Could not fetch alerts:", e);
      }
    })();
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6 text-red-600">Alert History 🚨</h1>
      <div className="space-y-4">
        {alerts.length === 0 && <p className="text-gray-500">No alerts yet.</p>}
        {alerts.map((a) => (
          <AlertItem key={a._id ?? a.timestamp} alert={a} />
        ))}
      </div>
    </div>
  );
};

export default AlertPage;
