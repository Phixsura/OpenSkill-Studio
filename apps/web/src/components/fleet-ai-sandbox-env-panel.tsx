"use client";
export function FleetAiSandboxEnvPanel({ envs, active, environments, sessions, lifetime }: { envs: number; active: number; environments: number; sessions: number; lifetime: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏖️ AI Sandbox Env</h3>
    <div className="text-sm">{active}/{envs} active · {environments} envs · {sessions.toLocaleString()} sessions · {lifetime}h lifetime</div>
  </div>);
}
