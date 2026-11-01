"use client";
export function FleetAiPlatRoadmapPanel({ roadmaps, active, planned, inProgress, completed }: { roadmaps: number; active: number; planned: number; inProgress: number; completed: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🗺️ AI Platform Roadmap</h3>
    <div className="text-sm">{active}/{roadmaps} active · {planned} planned · {inProgress} in progress · {completed} completed</div>
  </div>);
}
