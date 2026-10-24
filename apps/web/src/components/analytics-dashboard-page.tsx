"use client";

interface HealthIndicator { metric: string; status: string; value: number; }
interface AnalyticsDashboardPageProps { dauDisplay: string; mauDisplay: string;
  dauMauRatio: number; engagement: string; apiDisplay: string;
  revenueDisplay: string; newAppsMtd: number; avgSessionMin: number;
  npsScore: number; supportTicketsOpen: number; healthIndicators: HealthIndicator[]; }

const ENG_COLOR: Record<string, string> = { high: "text-green-600", medium: "text-yellow-600", low: "text-red-600" };

export function AnalyticsDashboardPage({ dauDisplay, mauDisplay, dauMauRatio, engagement,
  apiDisplay, revenueDisplay, newAppsMtd, avgSessionMin, npsScore, supportTicketsOpen, healthIndicators }: AnalyticsDashboardPageProps) {
  return (
    <div className="space-y-5">
      <h2 className="text-lg font-bold">📊 Platform Analytics</h2>
      <div className="grid grid-cols-5 gap-3">
        {[
          { label: "DAU", value: dauDisplay, icon: "👥" },
          { label: "MAU", value: mauDisplay, icon: "📈" },
          { label: "API Calls", value: apiDisplay, icon: "📡" },
          { label: "Revenue MTD", value: revenueDisplay, icon: "💰" },
          { label: "New Apps", value: String(newAppsMtd), icon: "📱" },
        ].map(m => (
          <div key={m.label} className="rounded-xl border p-3 text-center dark:border-gray-700">
            <p className="text-lg mb-0.5">{m.icon}</p>
            <p className="text-lg font-bold">{m.value}</p>
            <p className="text-xs text-gray-400">{m.label}</p>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className={`text-2xl font-bold ${ENG_COLOR[engagement] || ""}`}>{dauMauRatio}%</p>
          <p className="text-xs text-gray-400">DAU/MAU · {engagement} engagement</p>
        </div>
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{avgSessionMin}m</p>
          <p className="text-xs text-gray-400">Avg Session</p>
        </div>
        <div className="rounded-xl border p-4 text-center dark:border-gray-700">
          <p className="text-2xl font-bold">{npsScore}</p>
          <p className="text-xs text-gray-400">NPS Score</p>
        </div>
      </div>
      <div className="flex gap-3 text-xs">
        {healthIndicators.map(h => (
          <span key={h.metric} className={`px-2 py-1 rounded ${
            h.status === "excellent" ? "bg-green-100 text-green-700" :
            h.status === "good" ? "bg-blue-100 text-blue-700" : "bg-red-100 text-red-700"
          }`}>{h.metric}: {h.value}</span>
        ))}
        <span className="px-2 py-1 rounded bg-gray-100 text-gray-600">🎫 {supportTicketsOpen} open tickets</span>
      </div>
    </div>
  );
}
