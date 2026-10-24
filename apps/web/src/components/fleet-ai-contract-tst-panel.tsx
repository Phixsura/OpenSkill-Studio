"use client";
export function FleetAiContractTstPanel({ testers, active, contracts, verified, breaking }: { testers: number; active: number; contracts: number; verified: number; breaking: number; }) {
  return (<div className="rounded-xl border dark:border-gray-700 p-4">
    <h3 className="font-semibold mb-1">📜 AI Contract Test</h3>
    <div className="text-sm">{active}/{testers} active · {contracts} contracts · {verified.toLocaleString()} verified · {breaking} breaking</div>
  </div>);
}
