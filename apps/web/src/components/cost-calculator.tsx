"use client";

import { useState } from "react";

interface CostBreakdown { tier: string; units: number; rate: number; cost: number; }
interface CostCalculatorProps { tiers: { name: string; from: number; to: number | null; rate: number }[];
  onCalculate: (usage: number) => { totalCost: number; breakdown: CostBreakdown[] }; }

export function CostCalculator({ tiers, onCalculate }: CostCalculatorProps) {
  const [usage, setUsage] = useState(1000);
  const result = onCalculate(usage);

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Cost Estimator</h3>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Monthly Usage</label>
        <input type="range" min={0} max={50000} step={100} value={usage}
          onChange={e => setUsage(Number(e.target.value))} className="w-full" />
        <p className="text-sm font-mono text-center">{usage.toLocaleString()} requests</p>
      </div>
      <div className="rounded-xl border p-4 text-center dark:border-gray-700">
        <p className="text-3xl font-bold">${result.totalCost.toFixed(2)}</p>
        <p className="text-xs text-gray-400">estimated monthly cost</p>
      </div>
      <div className="space-y-1">
        {result.breakdown.map((b, i) => (
          <div key={i} className="flex justify-between text-sm">
            <span className="text-gray-500">{b.tier} ({b.units.toLocaleString()} × ${b.rate})</span>
            <span className="font-medium">${b.cost.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
