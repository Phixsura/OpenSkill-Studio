"use client";

interface HealthInfo { total_destinations: number; healthy_count: number; degraded_count: number; down_count: number; success_rate: number; avg_latency_ms: number; circuit_breakers_open: number; dead_letter_count: number; overall_status: string; }
interface Props { health: HealthInfo; appName: string; }

const statusBg: Record<string, string> = {
  healthy: "bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300",
  degraded: "bg-yellow-50 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300",
  critical: "bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300",
};

export default function APIWebhookHealthDashboardCard({ health: h, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💚 Webhook Health</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className={`rounded px-2 py-0.5 text-[11px] font-medium ${statusBg[h.overall_status] ?? ""}`}>{h.overall_status}</span>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center">
        {[
          { l: "Healthy", v: h.healthy_count },
          { l: "Degraded", v: h.degraded_count },
          { l: "Down", v: h.down_count },
          { l: "Success", v: `${h.success_rate}%` },
          { l: "Latency", v: `${h.avg_latency_ms}ms` },
          { l: "CB Open", v: h.circuit_breakers_open },
          { l: "Dead Letters", v: h.dead_letter_count },
        ].map((m) => (
          <div key={m.l} className="rounded-lg bg-gray-50 py-1 dark:bg-gray-800">
            <p className="text-xs font-bold text-gray-900 dark:text-gray-100">{m.v}</p>
            <p className="text-[7px] text-gray-500">{m.l}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
