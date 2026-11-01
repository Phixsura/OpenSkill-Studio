"use client";
export function FleetAiDataLabelPanel({ projects, active, labeled, pending, accuracy }: { projects: number; active: number; labeled: number; pending: number; accuracy: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏷️ AI Data Labeling</h3>
    <div className="text-sm">{active}/{projects} active · {labeled.toLocaleString()} labeled · {pending.toLocaleString()} pending · {accuracy}% accuracy</div>
  </div>);
}
