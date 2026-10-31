"use client";
export function FleetAiMtIsolatePanel({ systems, active, tenants, isolated, breaches }: { systems: number; active: number; tenants: number; isolated: number; breaches: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 AI Multi-Tenant Isolation</h3>
    <div className="text-sm">{active}/{systems} active · {isolated}/{tenants} isolated · {breaches} breaches</div>
  </div>);
}
