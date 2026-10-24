"use client";

interface Acquisition { installs: number; uninstalls: number; net: number; growth_pct: number; }
interface Engagement { dau: number; wau: number; mau: number; retention_30d: number; }
interface Performance { api_calls: number; errors: number; error_rate: number; avg_latency_ms: number; }
interface Revenue { total: number; mrr: number; arpu: number; }
interface AnalyticsOverviewDashboardProps { period: string; acquisition: Acquisition;
  engagement: Engagement; performance: Performance; revenue: Revenue; }

export function AnalyticsOverviewDashboard({ period, acquisition, engagement, performance, revenue }: AnalyticsOverviewDashboardProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold">Analytics Overview</h2>
        <span className="rounded bg-gray-100 px-2.5 py-0.5 text-xs dark:bg-gray-800">{period}</span>
      </div>
      {/* Acquisition */}
      <div>
        <h3 className="text-sm font-medium text-gray-500">📥 Acquisition</h3>
        <div className="mt-2 grid grid-cols-4 gap-2">
          <div className="rounded bg-gray-50 p-2 text-center dark:bg-gray-800">
            <p className="text-lg font-bold text-green-600">+{acquisition.installs.toLocaleString()}</p>
            <p className="text-[10px] text-gray-400">Installs</p></div>
          <div className="rounded bg-gray-50 p-2 text-center dark:bg-gray-800">
            <p className="text-lg font-bold text-red-500">-{acquisition.uninstalls}</p>
            <p className="text-[10px] text-gray-400">Uninstalls</p></div>
          <div className="rounded bg-gray-50 p-2 text-center dark:bg-gray-800">
            <p className="text-lg font-bold">{acquisition.net}</p>
            <p className="text-[10px] text-gray-400">Net</p></div>
          <div className="rounded bg-gray-50 p-2 text-center dark:bg-gray-800">
            <p className="text-lg font-bold">{acquisition.growth_pct}%</p>
            <p className="text-[10px] text-gray-400">Growth</p></div>
        </div>
      </div>
      {/* Engagement */}
      <div>
        <h3 className="text-sm font-medium text-gray-500">👥 Engagement</h3>
        <div className="mt-2 grid grid-cols-4 gap-2">
          {[{l: "DAU", v: engagement.dau}, {l: "WAU", v: engagement.wau},
            {l: "MAU", v: engagement.mau}, {l: "D30 Ret.", v: `${engagement.retention_30d}%`}].map(m => (
            <div key={m.l} className="rounded bg-gray-50 p-2 text-center dark:bg-gray-800">
              <p className="text-lg font-bold">{typeof m.v === "number" ? m.v.toLocaleString() : m.v}</p>
              <p className="text-[10px] text-gray-400">{m.l}</p></div>
          ))}
        </div>
      </div>
      {/* Revenue */}
      <div>
        <h3 className="text-sm font-medium text-gray-500">💰 Revenue</h3>
        <div className="mt-2 grid grid-cols-3 gap-2">
          {[{l: "Total", v: `$${revenue.total.toLocaleString()}`},
            {l: "MRR", v: `$${revenue.mrr.toLocaleString()}`},
            {l: "ARPU", v: `$${revenue.arpu}`}].map(m => (
            <div key={m.l} className="rounded bg-gray-50 p-2 text-center dark:bg-gray-800">
              <p className="text-lg font-bold text-green-600">{m.v}</p>
              <p className="text-[10px] text-gray-400">{m.l}</p></div>
          ))}
        </div>
      </div>
    </div>
  );
}
