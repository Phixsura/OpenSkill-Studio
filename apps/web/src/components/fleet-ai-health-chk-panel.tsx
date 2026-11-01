"use client";
export function FleetAiHealthChkPanel({ probes, healthy, degraded, down, latency }: { probes: number; healthy: number; degraded: number; down: number; latency: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💚 AI Health Check</h3>
    <div className="text-sm">🟢 {healthy} · 🟡 {degraded} · 🔴 {down} of {probes} · {latency}ms avg</div>
  </div>);
}
