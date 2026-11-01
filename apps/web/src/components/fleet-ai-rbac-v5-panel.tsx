"use client";
export function FleetAiRbacV5Panel({ engines, active, roles, permissions, evals }: { engines: number; active: number; roles: number; permissions: number; evals: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 AI RBAC v5</h3>
    <div className="text-sm">{active}/{engines} active · {roles} roles · {permissions} perms · {evals.toLocaleString()} evals</div>
  </div>);
}
