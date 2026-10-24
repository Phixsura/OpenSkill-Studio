"use client";
export function FleetAiTokBillV3Panel({ meters, active, tokens, revenue, customers }: { meters: number; active: number; tokens: number; revenue: number; customers: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">💰 AI Token Billing v3</h3>
    <div className="text-sm">{active}/{meters} active · {tokens.toLocaleString()} tokens · ${revenue.toLocaleString()} · {customers.toLocaleString()} customers</div>
  </div>);
}
