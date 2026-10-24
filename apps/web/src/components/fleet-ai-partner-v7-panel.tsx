"use client";
export function FleetAiPartnerV7Panel({ systems, active, partners, integrations, revenue }: { systems: number; active: number; partners: number; integrations: number; revenue: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤝 AI Partner v7</h3>
    <div className="text-sm">{active}/{systems} active · {partners} partners · {integrations.toLocaleString()} integrations · {revenue}% rev share</div>
  </div>);
}
