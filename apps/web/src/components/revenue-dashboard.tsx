"use client";

import { useState } from "react";

interface RevenueMetrics {
  grossCents: number;
  refundsCents: number;
  netCents: number;
  platformFeeCents: number;
  developerCents: number;
  mrr: number;
}

interface TierRevenue {
  tier: string;
  revenueCents: number;
}

interface TopExtension {
  extensionId: string;
  name: string;
  revenueCents: number;
}

function formatCurrency(cents: number): string {
  return `$${(cents / 100).toLocaleString("en-US", { minimumFractionDigits: 2 })}`;
}

export function RevenueDashboard({
  metrics,
  tiers,
  topExtensions,
  period,
}: {
  metrics: RevenueMetrics;
  tiers: TierRevenue[];
  topExtensions: TopExtension[];
  period: string;
}) {
  const [tab, setTab] = useState<"overview" | "tiers" | "top">("overview");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">💰 Revenue Dashboard</h2>
        <span className="text-sm text-gray-500">{period}</span>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Gross</span>
          <span className="text-lg font-bold text-green-600">{formatCurrency(metrics.grossCents)}</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">Net</span>
          <span className="text-lg font-bold">{formatCurrency(metrics.netCents)}</span>
        </div>
        <div className="rounded-xl border dark:border-gray-700 p-3 text-center">
          <span className="text-xs text-gray-500 block">MRR</span>
          <span className="text-lg font-bold text-blue-600">{formatCurrency(metrics.mrr)}</span>
        </div>
      </div>

      <div className="flex gap-1">
        {(["overview", "tiers", "top"] as const).map((t) => (
          <button key={t} onClick={() => setTab(t)}
            className={`text-xs px-3 py-1 rounded-lg ${tab === t ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {t === "overview" ? "Overview" : t === "tiers" ? "By Tier" : "Top Extensions"}
          </button>
        ))}
      </div>

      {tab === "overview" && (
        <div className="space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-gray-500">Refunds</span><span className="text-red-500">-{formatCurrency(metrics.refundsCents)}</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Platform Fee (15%)</span><span>{formatCurrency(metrics.platformFeeCents)}</span></div>
          <div className="flex justify-between font-semibold"><span>Developer Earnings</span><span className="text-green-600">{formatCurrency(metrics.developerCents)}</span></div>
        </div>
      )}

      {tab === "tiers" && (
        <div className="space-y-2">
          {tiers.map((t) => {
            const pct = metrics.grossCents > 0 ? (t.revenueCents / metrics.grossCents * 100).toFixed(1) : "0";
            return (
              <div key={t.tier} className="flex items-center justify-between rounded-lg border dark:border-gray-700 p-3">
                <span className="font-medium text-sm capitalize">{t.tier}</span>
                <div className="text-right">
                  <span className="text-sm font-bold">{formatCurrency(t.revenueCents)}</span>
                  <span className="text-xs text-gray-400 ml-1">({pct}%)</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {tab === "top" && (
        <div className="space-y-1">
          {topExtensions.map((ext, i) => (
            <div key={ext.extensionId} className="flex items-center gap-2 text-sm p-2">
              <span className="w-5 text-gray-400 font-mono">#{i + 1}</span>
              <span className="flex-1 font-medium">{ext.name}</span>
              <span className="font-bold">{formatCurrency(ext.revenueCents)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
