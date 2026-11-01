"use client";
export function FleetAiDriftDetPanel({ detectors, active, alerts, driftScore, retrained }: { detectors: number; active: number; alerts: number; driftScore: number; retrained: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📉 AI Drift Detection</h3>
    <div className="text-sm">{active}/{detectors} active · {alerts} alerts · drift {driftScore} · {retrained} retrained</div>
  </div>);
}
