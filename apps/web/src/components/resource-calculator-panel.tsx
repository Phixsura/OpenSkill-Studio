"use client";

import { useState } from "react";

interface ResourceEstimate {
  cpuCores: number; memoryMb: number; storageMb: number;
  bandwidthGb: number; estimatedCostCents: number; recommendedTier: string;
}

const tierColors: Record<string, string> = {
  free: "bg-gray-100 text-gray-700", starter: "bg-blue-100 text-blue-700",
  pro: "bg-purple-100 text-purple-700", enterprise: "bg-yellow-100 text-yellow-700",
};

function fmt(cents: number) { return `$${(cents / 100).toFixed(2)}`; }

export function ResourceCalculatorPanel({
  estimate, onCalculate,
}: {
  estimate: ResourceEstimate | null;
  onCalculate?: (users: number, features: string[]) => void;
}) {
  const [users, setUsers] = useState(100);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🧮 Resource Calculator</h2>
      <div className="flex gap-2">
        <input type="number" value={users} onChange={(e) => setUsers(parseInt(e.target.value) || 0)}
          className="rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm w-32" />
        <span className="text-sm text-gray-500 self-center">expected users</span>
        <button onClick={() => onCalculate?.(users, [])}
          className="text-sm bg-blue-600 text-white px-4 py-1.5 rounded-lg ml-auto">Calculate</button>
      </div>
      {estimate && (
        <>
          <div className="grid grid-cols-4 gap-2 text-center text-xs">
            <div className="rounded-lg border dark:border-gray-700 p-2">
              <span className="text-gray-500 block">CPU</span>
              <span className="font-bold">{estimate.cpuCores} cores</span>
            </div>
            <div className="rounded-lg border dark:border-gray-700 p-2">
              <span className="text-gray-500 block">Memory</span>
              <span className="font-bold">{estimate.memoryMb} MB</span>
            </div>
            <div className="rounded-lg border dark:border-gray-700 p-2">
              <span className="text-gray-500 block">Storage</span>
              <span className="font-bold">{estimate.storageMb} MB</span>
            </div>
            <div className="rounded-lg border dark:border-gray-700 p-2">
              <span className="text-gray-500 block">Bandwidth</span>
              <span className="font-bold">{estimate.bandwidthGb} GB</span>
            </div>
          </div>
          <div className="flex items-center justify-between rounded-xl border dark:border-gray-700 p-4">
            <div>
              <span className="text-sm text-gray-500">Estimated Cost</span>
              <span className="text-2xl font-bold block">{fmt(estimate.estimatedCostCents)}/mo</span>
            </div>
            <span className={`text-sm px-3 py-1 rounded-full font-bold capitalize ${tierColors[estimate.recommendedTier] || ""}`}>
              {estimate.recommendedTier}
            </span>
          </div>
        </>
      )}
    </div>
  );
}
