"use client";
export function FleetAiTimeoutPanel({ managers, active, timeouts, defaultMs, adaptive }: { managers: number; active: number; timeouts: number; defaultMs: number; adaptive: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">⏱️ AI Timeout Manager</h3>
    <div className="text-sm">{active}/{managers} active · {timeouts} timeouts · {defaultMs}ms default · {adaptive} adaptive</div>
  </div>);
}
