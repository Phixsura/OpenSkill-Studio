"use client";
export function FleetAiMoePanel({ routers, active, experts, tokens, loadBalance }: { routers: number; active: number; experts: number; tokens: number; loadBalance: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🧩 AI Mixture of Experts</h3>
    <div className="text-sm">{active}/{routers} active · {experts} experts · {tokens.toLocaleString()} tok · balance {loadBalance}</div>
  </div>);
}
