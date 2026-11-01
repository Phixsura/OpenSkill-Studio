"use client";
export function FleetCapPlanPanel({ totalResources, needsExpansion, costDelta, actionNeeded }: { totalResources: number; needsExpansion: number; costDelta: number; actionNeeded: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Capacity Planning</h3>
    <div className="text-sm">{needsExpansion}/{totalResources} need expansion</div>
    {actionNeeded && <span className="text-xs text-yellow-600">💰 +${costDelta.toLocaleString()} estimated</span>}
  </div>);
}
