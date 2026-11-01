"use client";
export function FleetAiPlatformVisionV7Panel({ planners, active, goals, achieved, horizon }: { planners: number; active: number; goals: number; achieved: number; horizon: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔭 AI Platform Vision v7</h3>
    <div className="text-sm">{active}/{planners} active · {achieved}/{goals} goals · {horizon}yr horizon</div>
  </div>);
}
