"use client";

interface DashboardSummaryGridProps {
  totalApps: number; published: number; apiCalls: number;
  executions: number; webhooks: number; avgHealth: number;
}

export function DashboardSummaryGrid({ totalApps, published, apiCalls, executions, webhooks, avgHealth }: DashboardSummaryGridProps) {
  const items = [
    { label: "Apps", value: totalApps, icon: "📦" },
    { label: "Published", value: published, icon: "🚀" },
    { label: "API Calls", value: apiCalls.toLocaleString(), icon: "🔗" },
    { label: "Executions", value: executions.toLocaleString(), icon: "⚡" },
    { label: "Webhooks", value: webhooks.toLocaleString(), icon: "🔔" },
    { label: "Health", value: `${avgHealth}%`, icon: avgHealth >= 80 ? "💚" : "⚠️" },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      {items.map(i => (
        <div key={i.label} className="rounded-lg border border-gray-200 p-3 text-center dark:border-gray-700">
          <span className="text-xl">{i.icon}</span>
          <p className="text-lg font-bold">{i.value}</p>
          <p className="text-xs text-gray-500">{i.label}</p>
        </div>
      ))}
    </div>
  );
}
