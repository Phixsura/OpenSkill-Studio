"use client";
export function FleetAiEnterpriseV7Panel({ systems, active, enterprise, sla, certs, tiers }: { systems: number; active: number; enterprise: number; sla: number; certs: number; tiers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🏢 AI Enterprise v7</h3>
    <div className="text-sm">{active}/{systems} active · {enterprise.toLocaleString()} enterprise · {sla}% SLA · {certs} certs · {tiers} tiers</div>
  </div>);
}
