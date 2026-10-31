"use client";
export function FleetFeastPanel({ projects, active, featureViews, entities }: { projects: number; active: number; featureViews: number; entities: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🍽️ Feast</h3>
    <div className="text-sm">{active}/{projects} active · {featureViews} views · {entities} entities</div>
  </div>);
}
