"use client";
export function FleetAiExpTrackPanel({ trackers, active, experiments, runs, bestMetric }: { trackers: number; active: number; experiments: number; runs: number; bestMetric: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧪 AI Experiment Tracker</h3>
    <div className="text-sm">{active}/{trackers} active · {experiments} experiments · {runs.toLocaleString()} runs · best {bestMetric}%</div>
  </div>);
}
