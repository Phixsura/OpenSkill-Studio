"use client";
export function FleetAiExpVerPanel({ systems, active, experiments, snapshots, reproducible }: { systems: number; active: number; experiments: number; snapshots: number; reproducible: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔬 AI Experiment Versioning</h3>
    <div className="text-sm">{active}/{systems} active · {experiments} experiments · {snapshots.toLocaleString()} snapshots · {reproducible}% reproducible</div>
  </div>);
}
