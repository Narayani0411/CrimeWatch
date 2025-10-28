import React, { useEffect, useState } from "react";

const AlertItem = ({ alert }) => {
  return (
    <div className="p-3 bg-red-100 border-l-4 border-red-500 rounded shadow-sm">
      <p className="text-sm text-gray-700">
        <span className="font-semibold text-red-700">Timestamp:</span> {alert.timestamp}
      </p>
    </div>
  );
};

const AlertPage = ({ initialAlerts = [] }) => {
  const [alerts, setAlerts] = useState(initialAlerts);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("http://localhost:8000/alerts/");
        if (res.ok) {
          const data = await res.json();
          console.log(data)

          // ✅ Filter only alerts with "weapon" or "violence"
          const filtered = (data.alerts || []).filter((a) => {
            const d = (a.danger_status || "").toLowerCase();
            return d.includes("weapon") || d.includes("violence");
          });

          setAlerts(filtered);
        }
      } catch (e) {
        console.warn("Could not fetch alerts:", e);
      }
    })();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6 text-red-600 text-center">🚨 Weapon & Violence Alerts</h1>
      <div className="space-y-3">
        {alerts.length === 0 ? (
          <p className="text-gray-500 text-center">No weapon or violence alerts yet.</p>
        ) : (
          alerts.map((a) => <AlertItem key={a._id ?? a.timestamp} alert={a} />)
        )}
      </div>
    </div>
  );
};

export default AlertPage;