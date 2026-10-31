"use client";
export function FleetKubecostPanel({ clusters, monthlyCost, savingsAvailable, savingsPct }: { clusters: number; monthlyCost: number; savingsAvailable: number; savingsPct: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💲 Kubecost</h3>
    <div className="text-sm">${monthlyCost.toLocaleString()}/mo · ${savingsAvailable.toLocaleString()} savings ({savingsPct}%)</div>
  </div>);
}
