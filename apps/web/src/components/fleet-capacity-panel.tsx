"use client";
export function FleetCapacityPanel({ avgCpu, headroom, needsScaling }: { avgCpu: number; headroom: number; needsScaling: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📊 Fleet Capacity</h3>
    <div className="text-sm">{avgCpu}% avg CPU · {headroom}% headroom</div>
    {needsScaling && <span className="text-xs text-red-500">⚠️ Scaling needed</span>}
  </div>);
}
