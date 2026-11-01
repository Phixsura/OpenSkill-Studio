"use client";

interface PlatformDashboardSummaryProps {
  totalApps: number; totalDevelopers: number; totalUsers: number; totalInstalls: number;
  mrr: number; arr: number; growthPct: number; uptimePct: number; avgLatencyMs: number;
  dau: number; mau: number; retention30d: number; status: string;
}

export function PlatformDashboardSummary(p: PlatformDashboardSummaryProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Platform Dashboard</h1>
        <span className={`rounded-full px-3 py-1 text-sm font-medium ${p.status === "operational" ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {p.status === "operational" ? "🟢 Operational" : "🔴 Degraded"}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: "Apps", value: p.totalApps.toLocaleString(), color: "text-blue-600" },
          { label: "Developers", value: p.totalDevelopers.toLocaleString(), color: "text-purple-600" },
          { label: "Users", value: p.totalUsers.toLocaleString(), color: "text-green-600" },
          { label: "Installs", value: p.totalInstalls.toLocaleString(), color: "text-orange-600" },
        ].map(m => (
          <div key={m.label} className="rounded-lg border p-3 text-center dark:border-gray-700">
            <p className={`text-2xl font-bold ${m.color}`}>{m.value}</p>
            <p className="text-xs text-gray-400">{m.label}</p>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg bg-green-50 p-4 text-center dark:bg-green-900/10">
          <p className="text-xl font-bold text-green-600">${p.mrr.toLocaleString()}</p>
          <p className="text-xs text-gray-400">MRR ({p.growthPct > 0 ? "+" : ""}{p.growthPct}%)</p>
        </div>
        <div className="rounded-lg bg-blue-50 p-4 text-center dark:bg-blue-900/10">
          <p className="text-xl font-bold">{p.uptimePct}%</p>
          <p className="text-xs text-gray-400">Uptime · {p.avgLatencyMs}ms</p>
        </div>
        <div className="rounded-lg bg-purple-50 p-4 text-center dark:bg-purple-900/10">
          <p className="text-xl font-bold">{p.dau.toLocaleString()}</p>
          <p className="text-xs text-gray-400">DAU · {p.retention30d}% ret.</p>
        </div>
      </div>
    </div>
  );
}
