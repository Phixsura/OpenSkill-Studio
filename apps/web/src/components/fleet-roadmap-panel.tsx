"use client";
export function FleetRoadmapPanel({ total, done, inProgress, planned, completionPct }: { total: number; done: number; inProgress: number; planned: number; completionPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗺️ Roadmap</h3>
    <div className="text-sm">✅ {done} · 🔄 {inProgress} · 📋 {planned} ({completionPct}% done)</div>
  </div>);
}
