"use client";
export function FleetHoneycombPanel({ datasets, active, eventsPerSec, queries }: { datasets: number; active: number; eventsPerSec: number; queries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🍯 Honeycomb</h3>
    <div className="text-sm">{active}/{datasets} active · {eventsPerSec.toLocaleString()} eps · {queries} queries/24h</div>
  </div>);
}
