"use client";
export function FleetAiRoadmapV7Panel({ roadmaps, active, planned, inProgress, shipped, onTime }: { roadmaps: number; active: number; planned: number; inProgress: number; shipped: number; onTime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗺️ AI Roadmap v7</h3>
    <div className="text-sm">{active}/{roadmaps} active · {planned} planned · {inProgress} WIP · {shipped} shipped · {onTime}% on time</div>
  </div>);
}
