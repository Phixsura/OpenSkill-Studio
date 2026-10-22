"use client";

interface CostBreakdownCardProps {
  totalUsd: number;
  breakdown: { api: number; storage: number; bandwidth: number; compute: number };
}

export function CostBreakdownCard({ totalUsd, breakdown }: CostBreakdownCardProps) {
  const items = [
    { label: "API Calls", cost: breakdown.api, icon: "🌐" },
    { label: "Storage", cost: breakdown.storage, icon: "💾" },
    { label: "Bandwidth", cost: breakdown.bandwidth, icon: "📡" },
    { label: "Compute", cost: breakdown.compute, icon: "⚡" },
  ];

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Estimated Monthly Cost</h3>
        <span className="text-xl font-bold">${totalUsd.toFixed(2)}</span>
      </div>
      <ul className="mt-3 space-y-2">
        {items.map(i => (
          <li key={i.label} className="flex items-center justify-between text-sm">
            <span>{i.icon} {i.label}</span>
            <span className={i.cost > 0 ? "font-medium" : "text-gray-400"}>${i.cost.toFixed(2)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
