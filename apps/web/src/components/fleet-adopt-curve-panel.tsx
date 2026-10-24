"use client";
export function FleetAdoptCurvePanel({ months, currentUsers, growthPct, accelerating }: { months: number; currentUsers: number; growthPct: number; accelerating: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📈 Adoption Curve</h3>
    <div className="text-sm">{currentUsers.toLocaleString()} users · {growthPct}% growth · {months} months</div>
    {accelerating && <span className="text-xs text-green-600">🚀 Accelerating!</span>}
  </div>);
}
