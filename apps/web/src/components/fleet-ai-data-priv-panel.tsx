"use client";
export function FleetAiDataPrivPanel({ systems, active, epsilon, datasets, queries }: { systems: number; active: number; epsilon: number; datasets: number; queries: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔐 AI Data Privacy</h3>
    <div className="text-sm">{active}/{systems} active · ε={epsilon} · {datasets} datasets · {queries.toLocaleString()} queries</div>
  </div>);
}
