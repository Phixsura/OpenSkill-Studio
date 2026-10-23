"use client";

interface KPI { label: string; value: string | number; trend?: string; icon: string; }
interface MarketplaceKpiDashboardProps { kpis: KPI[]; opportunities: string[]; }

export function MarketplaceKpiDashboard({ kpis, opportunities }: MarketplaceKpiDashboardProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {kpis.map(k => (
          <div key={k.label} className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
            <span className="text-xl">{k.icon}</span>
            <p className="mt-1 text-xl font-bold">{typeof k.value === "number" ? k.value.toLocaleString() : k.value}</p>
            <p className="text-xs text-gray-400">{k.label}</p>
            {k.trend && <p className="text-xs text-green-600">{k.trend}</p>}
          </div>
        ))}
      </div>
      {opportunities.length > 0 && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-900/20">
          <p className="text-xs font-semibold text-blue-700 dark:text-blue-300">💡 Growth Opportunities</p>
          <ul className="mt-1 space-y-0.5">
            {opportunities.map((o, i) => <li key={i} className="text-xs text-blue-600 dark:text-blue-400">• {o}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}
