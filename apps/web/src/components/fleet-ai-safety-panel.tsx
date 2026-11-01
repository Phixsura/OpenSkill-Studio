"use client";
export function FleetAiSafetyPanel({ monitors, active, violations, checks }: { monitors: number; active: number; violations: number; checks: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Safety</h3>
    <div className="text-sm">{active}/{monitors} active · {checks.toLocaleString()} checks · {violations} violations</div>
  </div>);
}
