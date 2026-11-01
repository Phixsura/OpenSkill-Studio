"use client";
export function FleetKubesharkPanel({ total, active, requestsCaptured, anomalies }: { total: number; active: number; requestsCaptured: number; anomalies: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🦈 Kubeshark</h3>
    <div className="text-sm">{active}/{total} active · {requestsCaptured.toLocaleString()} captured</div>
    {anomalies > 0 && <span className="text-xs text-yellow-600">⚠️ {anomalies} anomalies</span>}
  </div>);
}
