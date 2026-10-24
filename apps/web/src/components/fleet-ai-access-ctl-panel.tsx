"use client";
export function FleetAiAccessCtlPanel({ controllers, active, policies, evaluations, denied }: { controllers: number; active: number; policies: number; evaluations: number; denied: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔒 AI Access Control</h3>
    <div className="text-sm">{active}/{controllers} active · {policies} policies · {evaluations.toLocaleString()} evals · {denied.toLocaleString()} denied</div>
  </div>);
}
