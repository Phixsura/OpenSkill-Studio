"use client";
export function FleetAiGuardPanel({ services, active, checks, blocked, blockRate }: { services: number; active: number; checks: number; blocked: number; blockRate: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ AI Guardrails</h3>
    <div className="text-sm">{active}/{services} active · {checks.toLocaleString()} checks · {blocked} blocked ({blockRate}%)</div>
  </div>);
}
