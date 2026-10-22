"use client";

interface AppStats {
  total_installs: number;
  active_installs: number;
  total_executions: number;
  execution_success_rate: number;
  total_webhooks: number;
  webhook_success_rate: number;
  total_api_calls: number;
  error_count: number;
}

interface AppStatsDashboardProps {
  stats: AppStats;
}

function StatCard({ label, value, suffix }: { label: string; value: number | string; suffix?: string }) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
      <p className="text-2xl font-bold">{typeof value === "number" ? value.toLocaleString() : value}{suffix}</p>
    </div>
  );
}

export function AppStatsDashboard({ stats }: AppStatsDashboardProps) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <StatCard label="Active Installs" value={stats.active_installs} />
      <StatCard label="Total Executions" value={stats.total_executions} />
      <StatCard label="Success Rate" value={stats.execution_success_rate} suffix="%" />
      <StatCard label="API Calls" value={stats.total_api_calls} />
      <StatCard label="Webhooks Sent" value={stats.total_webhooks} />
      <StatCard label="Webhook Success" value={stats.webhook_success_rate} suffix="%" />
      <StatCard label="Errors" value={stats.error_count} />
      <StatCard label="Total Installs" value={stats.total_installs} />
    </div>
  );
}
