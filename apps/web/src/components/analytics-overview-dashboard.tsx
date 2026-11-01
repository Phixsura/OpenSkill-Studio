"use client";

interface AnalyticsOverview {
  engagement: { dau: number; wau: number; mau: number; dauWauRatio: number; avgSession: number; retention7d: number };
  growth: { extensionsToday: number; installsToday: number; newDevsToday: number };
  revenue: { todayCents: number; projectedMonthly: number };
  api: { callsToday: number };
  satisfaction: { nps: number };
}

function fmt(cents: number) { return `$${(cents / 100).toLocaleString()}`; }

export function AnalyticsOverviewDashboard({ data }: { data: AnalyticsOverview }) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">📊 Platform Analytics</h2>

      <div className="grid grid-cols-3 gap-3 sm:grid-cols-6">
        {[
          { l: "DAU", v: data.engagement.dau.toLocaleString(), i: "👥" },
          { l: "WAU", v: data.engagement.wau.toLocaleString(), i: "📅" },
          { l: "MAU", v: data.engagement.mau.toLocaleString(), i: "📆" },
          { l: "Installs", v: data.growth.installsToday, i: "📥" },
          { l: "Revenue", v: fmt(data.revenue.todayCents), i: "💰" },
          { l: "API Calls", v: data.api.callsToday.toLocaleString(), i: "📡" },
        ].map((m) => (
          <div key={m.l} className="rounded-xl border dark:border-gray-700 p-3 text-center">
            <span className="text-xl block">{m.i}</span>
            <span className="font-bold text-sm block">{m.v}</span>
            <span className="text-[10px] text-gray-500">{m.l}</span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-4 gap-2 text-center text-xs">
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">DAU/WAU</span>
          <span className={`font-bold ${data.engagement.dauWauRatio >= 40 ? "text-green-600" : "text-yellow-600"}`}>{data.engagement.dauWauRatio}%</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Retention</span>
          <span className="font-bold">{data.engagement.retention7d}%</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">Avg Session</span>
          <span className="font-bold">{data.engagement.avgSession}min</span>
        </div>
        <div className="rounded-lg border dark:border-gray-700 p-2">
          <span className="text-gray-500 block">NPS</span>
          <span className={`font-bold ${data.satisfaction.nps >= 50 ? "text-green-600" : "text-yellow-600"}`}>{data.satisfaction.nps}</span>
        </div>
      </div>
    </div>
  );
}
