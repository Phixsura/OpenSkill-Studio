"use client";
export function FleetAiSmokeTestPanel({ testers, active, runs, passRate, duration }: { testers: number; active: number; runs: number; passRate: number; duration: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💨 AI Smoke Test</h3>
    <div className="text-sm">{active}/{testers} active · {runs.toLocaleString()} runs · {passRate}% pass · {duration}s</div>
  </div>);
}
