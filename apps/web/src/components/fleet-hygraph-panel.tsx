"use client";
export function FleetHygraphPanel({ projects, active, models, entries }: { projects: number; active: number; models: number; entries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📋 Hygraph</h3>
    <div className="text-sm">{active}/{projects} active · {models} models · {entries.toLocaleString()} entries</div>
  </div>);
}
