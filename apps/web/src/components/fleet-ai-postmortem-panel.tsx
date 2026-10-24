"use client";
export function FleetAiPostmortemPanel({ systems, active, postmortems, actionItems, completed, rate }: { systems: number; active: number; postmortems: number; actionItems: number; completed: number; rate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📝 AI Postmortem</h3>
    <div className="text-sm">{active}/{systems} active · {postmortems} postmortems · {completed}/{actionItems} items ({rate}%)</div>
  </div>);
}
