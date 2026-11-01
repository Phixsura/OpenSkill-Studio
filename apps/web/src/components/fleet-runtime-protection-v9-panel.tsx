"use client";
export function FleetRuntimeProtectionV9Panel({ agents, blocked }: { agents: number; blocked: number }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🛡️ Runtime Protection v9</h3>
    <div className="text-sm">{agents} agents · {blocked} threats blocked</div>
  </div>);
}
