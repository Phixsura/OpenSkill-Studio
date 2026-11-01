"use client";
export function FleetAiTestGenPanel({ generators, active, tests, coverageBoost, passRate }: { generators: number; active: number; tests: number; coverageBoost: number; passRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧪 AI Test Generation</h3>
    <div className="text-sm">{active}/{generators} active · {tests.toLocaleString()} tests · +{coverageBoost}% coverage · {passRate}% pass</div>
  </div>);
}
