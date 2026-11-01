"use client";
export function FleetStatuspageIoPanel({ pages, operational, degraded, activeIncidents }: { pages: number; operational: number; degraded: number; activeIncidents: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📡 StatusPage</h3>
    <div className="text-sm">🟢 {operational} · 🟡 {degraded} · {activeIncidents} incidents</div>
  </div>);
}
