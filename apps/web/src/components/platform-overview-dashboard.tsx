"use client";

interface MetricValue { value: number; display: string; }
interface PlatformOverviewDashboardProps {
  healthDisplay: string; status: string;
  metrics: Record<string, MetricValue>; milestone: string;
}

const METRIC_CONFIG: Record<string, { label: string; icon: string }> = {
  apps: { label: "Apps", icon: "📱" }, developers: { label: "Developers", icon: "👩‍💻" },
  api_calls_24h: { label: "API Calls (24h)", icon: "📡" }, uptime: { label: "Uptime", icon: "🟢" },
  mrr: { label: "MRR", icon: "💰" }, webhooks: { label: "Webhooks", icon: "🔗" },
  error_rate: { label: "Error Rate", icon: "❌" }, latency: { label: "Latency", icon: "⏱️" },
  deploys_today: { label: "Deploys Today", icon: "🚀" }, incidents: { label: "Incidents", icon: "🚨" },
};

const STATUS_STYLE: Record<string, string> = {
  excellent: "bg-green-100 text-green-700", good: "bg-blue-100 text-blue-700",
  fair: "bg-yellow-100 text-yellow-700", poor: "bg-red-100 text-red-700",
};

export function PlatformOverviewDashboard({ healthDisplay, status, metrics, milestone }: PlatformOverviewDashboardProps) {
  return (
    <div className="space-y-5">
      <div className="rounded-xl border p-6 dark:border-gray-700 text-center">
        <h2 className="text-xl font-bold mb-2">🏠 Platform Overview</h2>
        <p className="text-4xl font-bold mb-1">{healthDisplay}</p>
        <span className={`text-sm px-3 py-1 rounded-full font-medium ${STATUS_STYLE[status] || ""}`}>
          {status}
        </span>
      </div>
      <div className="grid grid-cols-5 gap-3">
        {Object.entries(metrics).map(([key, m]) => {
          const cfg = METRIC_CONFIG[key] || { label: key, icon: "📌" };
          return (
            <div key={key} className="rounded-xl border p-3 text-center dark:border-gray-700">
              <p className="text-lg mb-0.5">{cfg.icon}</p>
              <p className="text-lg font-bold">{m.display}</p>
              <p className="text-xs text-gray-400">{cfg.label}</p>
            </div>
          );
        })}
      </div>
      <div className="rounded-lg bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 p-4 text-center text-sm font-medium">
        {milestone}
      </div>
    </div>
  );
}
