"use client";

import { useState } from "react";

interface EndpointUsage {
  endpoint: string;
  calls: number;
  bytes: number;
}

interface Invoice {
  id: string;
  periodStart: string;
  periodEnd: string;
  totalCalls: number;
  totalCostCents: number;
  status: string;
}

function fmt(cents: number) {
  return `$${(cents / 100).toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
}

function fmtBytes(b: number) {
  if (b < 1024) return `${b}B`;
  if (b < 1048576) return `${(b / 1024).toFixed(1)}KB`;
  return `${(b / 1048576).toFixed(1)}MB`;
}

export function UsageBillingPanel({
  endpoints,
  invoices,
  totalCalls,
  estimatedCostCents,
  freeTierRemaining,
}: {
  endpoints: EndpointUsage[];
  invoices: Invoice[];
  totalCalls: number;
  estimatedCostCents: number;
  freeTierRemaining: number;
}) {
  const [tab, setTab] = useState<"usage" | "invoices">("usage");

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">💳 API Usage & Billing</h2>

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Total Calls</span>
          <span className="text-lg font-bold">{totalCalls.toLocaleString()}</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Est. Cost</span>
          <span className="text-lg font-bold text-blue-600">{fmt(estimatedCostCents)}</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Free Tier Left</span>
          <span className="text-lg font-bold text-green-600">{freeTierRemaining.toLocaleString()}</span>
        </div>
      </div>

      <div className="flex gap-1">
        {(["usage", "invoices"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "usage" ? "Usage by Endpoint" : `Invoices (${invoices.length})`}
          </button>
        ))}
      </div>

      {tab === "usage" && (
        <div className="space-y-1">
          {endpoints.map((ep) => (
            <div key={ep.endpoint} className="flex items-center justify-between rounded-lg border dark:border-gray-700 p-3">
              <code className="text-sm">{ep.endpoint}</code>
              <div className="text-xs text-gray-500">
                <span className="font-bold mr-2">{ep.calls.toLocaleString()} calls</span>
                <span>{fmtBytes(ep.bytes)}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "invoices" && (
        <div className="space-y-2">
          {invoices.map((inv) => (
            <div key={inv.id} className="rounded-lg border dark:border-gray-700 p-3 flex items-center justify-between">
              <div>
                <span className="text-sm font-medium">{inv.periodStart} — {inv.periodEnd}</span>
                <span className="text-xs text-gray-500 ml-2">{inv.totalCalls.toLocaleString()} calls</span>
              </div>
              <span className="font-bold text-sm">{fmt(inv.totalCostCents)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
