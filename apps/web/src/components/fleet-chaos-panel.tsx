"use client";
export function FleetChaosPanel({ total, passed, weaknessesFound, resilient }: { total: number; passed: number; weaknessesFound: number; resilient: boolean; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🌪️ Chaos Engineering</h3>
    <div className="text-sm">{passed}/{total} passed · {weaknessesFound} weaknesses</div>
    <span className={`text-xs ${resilient ? "text-green-600" : "text-yellow-600"}`}>{resilient ? "✅ Resilient" : "⚠️ Issues found"}</span>
  </div>);
}
