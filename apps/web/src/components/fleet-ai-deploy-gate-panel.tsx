"use client";
export function FleetAiDeployGatePanel({ gates, active, evals, passed, blocked, checks }: { gates: number; active: number; evals: number; passed: number; blocked: number; checks: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🚧 AI Deployment Gate</h3>
    <div className="text-sm">{active}/{gates} active · {evals} evals · ✅ {passed} · 🚫 {blocked} · {checks} checks</div>
  </div>);
}
