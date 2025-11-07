import React, { useEffect, useState } from "react";

const AlertItem = ({ alert }) => (
  <div className="card border-l-8 border-pink-400 bg-pink-50 dark:bg-pink-900/30 fade-in">
    <p className="text-sm">
      <span className="font-semibold">⚠️ Timestamp:</span> {alert.timestamp}
    </p>
  </div>
);

const AlertPage = () => {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("http://localhost:8000/alerts/");
        if (res.ok) {
          const data = await res.json();
          const filtered = (data.alerts || []).filter((a) => {
            const d = (a.danger_status || "").toLowerCase();
            return d.includes("weapon") || d.includes("violence");
          });
          setAlerts(filtered);
        }
      } catch (err) {
        console.error("Error fetching alerts", err);
      }
    })();
  }, []);

  return (
    <div className="fade-in">
      <h1 className="text-3xl font-bold mb-6 text-pink-600 dark:text-pink-400 text-center">
        🚨 Weapon & Violence Alerts
      </h1>
      {alerts.length === 0 ? (
        <p className="text-gray-500 text-center">No alerts yet.</p>
      ) : (
        <div className="space-y-4">
          {alerts.map((a) => (
            <AlertItem key={a._id ?? a.timestamp} alert={a} />
          ))}
        </div>
      )}
    </div>
  );
};

export default AlertPage;
