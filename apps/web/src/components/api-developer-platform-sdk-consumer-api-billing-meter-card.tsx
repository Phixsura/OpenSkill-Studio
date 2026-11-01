"use client";

import { useState } from "react";

interface BillSummary {
  consumerId: string;
  period: string;
  totalUnits: number;
  billableUnits: number;
  totalDollars: number;
}

export default function BillingMeterCard() {
  const [bills] = useState<BillSummary[]>([
    { consumerId: "c-acme", period: "Oct 2024", totalUnits: 45200, billableUnits: 35200, totalDollars: 89.99 },
    { consumerId: "c-beta", period: "Oct 2024", totalUnits: 8500, billableUnits: 0, totalDollars: 29.99 },
  ]);

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
        Billing Meter
      </h3>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
        Usage-based billing with tiered pricing
      </p>

      <div className="mt-4 space-y-3">
        {bills.map((b) => (
          <div key={b.consumerId} className="rounded-lg border border-zinc-100 p-3 dark:border-zinc-700">
            <div className="flex items-center justify-between">
              <span className="font-mono text-sm text-zinc-800 dark:text-zinc-200">{b.consumerId}</span>
              <span className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
                ${b.totalDollars.toFixed(2)}
              </span>
            </div>
            <div className="mt-1 flex justify-between text-xs text-zinc-400">
              <span>{b.totalUnits.toLocaleString()} total units</span>
              <span>{b.billableUnits.toLocaleString()} billable</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {bills.length} consumers billed
      </div>
    </div>
  );
}
