"use client";
export function FleetAiCustomerV7Panel({ systems, active, customers, csat, nps, churn }: { systems: number; active: number; customers: number; csat: number; nps: number; churn: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🤝 AI Customer v7</h3>
    <div className="text-sm">{active}/{systems} active · {customers.toLocaleString()} customers · CSAT {csat} · NPS {nps} · {churn}% churn</div>
  </div>);
}
