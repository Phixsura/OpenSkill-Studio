"use client";

import { useState } from "react";

interface Tier { range: string; rate: number; taxable_amount: number; fee: number; }
interface PricingCalculatorWidgetProps { onCalculate: (revenue: number) => { totalFee: number; netRevenue: number; effectiveRate: number; breakdown: Tier[] }; }

export function PricingCalculatorWidget({ onCalculate }: PricingCalculatorWidgetProps) {
  const [revenue, setRevenue] = useState(10000);
  const result = onCalculate(revenue);

  return (
    <div className="space-y-4 rounded-lg border p-5 dark:border-gray-700">
      <h2 className="text-lg font-semibold">Pricing Calculator</h2>
      <div>
        <label className="text-sm text-gray-500">Monthly Revenue ($)</label>
        <input type="range" min={0} max={200000} step={1000} value={revenue}
          onChange={e => setRevenue(Number(e.target.value))}
          className="mt-1 w-full" />
        <p className="text-center text-xl font-bold">${revenue.toLocaleString()}</p>
      </div>
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-sm font-bold text-red-600">${result.totalFee.toLocaleString()}</p>
          <p className="text-xs text-gray-400">Platform Fee</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-sm font-bold text-green-600">${result.netRevenue.toLocaleString()}</p>
          <p className="text-xs text-gray-400">You Keep</p>
        </div>
        <div className="rounded bg-gray-50 p-2 dark:bg-gray-800">
          <p className="text-sm font-bold">{result.effectiveRate}%</p>
          <p className="text-xs text-gray-400">Effective Rate</p>
        </div>
      </div>
    </div>
  );
}
