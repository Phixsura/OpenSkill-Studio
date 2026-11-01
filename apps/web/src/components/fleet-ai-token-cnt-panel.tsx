"use client";
export function FleetAiTokenCntPanel({ accounts, inputTokens, outputTokens, totalCost }: { accounts: number; inputTokens: number; outputTokens: number; totalCost: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">🔢 Token Counter</h3>
    <div className="text-sm">{accounts} accounts · ↓{inputTokens.toLocaleString()} ↑{outputTokens.toLocaleString()} · ${totalCost.toLocaleString()}</div>
  </div>);
}
