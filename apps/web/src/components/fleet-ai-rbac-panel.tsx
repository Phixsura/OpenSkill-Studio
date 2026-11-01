"use client";
export function FleetAiRbacPanel({ engines, active, roles, policies, evals }: { engines: number; active: number; roles: number; policies: number; evals: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 AI RBAC</h3>
    <div className="text-sm">{active}/{engines} active · {roles} roles · {policies} policies · {evals.toLocaleString()} evals</div>
  </div>);
}
