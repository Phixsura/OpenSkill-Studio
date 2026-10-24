"use client";
export function FleetAiErrHandlerPanel({ handlers, active, errors, recovered, escalated, recoveryRate }: { handlers: number; active: number; errors: number; recovered: number; escalated: number; recoveryRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚨 AI Error Handler</h3>
    <div className="text-sm">{active}/{handlers} active · {errors} errors · {recovered} recovered · {escalated} escalated · {recoveryRate}%</div>
  </div>);
}
