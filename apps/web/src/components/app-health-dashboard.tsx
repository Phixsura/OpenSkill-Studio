"use client";

interface UptimeWindow {
  window_hours: number;
  total_checks: number;
  successful_checks: number;
  uptime_pct: number;
  downtime_minutes: number;
}

interface SLACompliance {
  target_pct: number;
  actual_pct: number;
  compliant: boolean;
  budget_remaining_minutes: number;
}

interface HealthEvent {
  status: "healthy" | "degraded" | "down" | "unknown";
  timestamp: string;
  reason: string | null;
}

interface AppHealthData {
  installation_id: string;
  app_name: string;
  current_status: "healthy" | "degraded" | "down" | "unknown";
  last_heartbeat_at: string | null;
  consecutive_failures: number;
  uptime_24h: UptimeWindow;
  uptime_7d: UptimeWindow;
  uptime_30d: UptimeWindow;
  sla_compliance: SLACompliance;
  recent_events: HealthEvent[];
}

interface AppHealthDashboardProps {
  health: AppHealthData;
}

const STATUS_STYLES: Record<string, { label: string; color: string; bg: string; ring: string }> = {
  healthy: {
    label: "Healthy",
    color: "text-green-700 dark:text-green-300",
    bg: "bg-green-50 dark:bg-green-900/20",
    ring: "ring-green-500",
  },
  degraded: {
    label: "Degraded",
    color: "text-yellow-700 dark:text-yellow-300",
    bg: "bg-yellow-50 dark:bg-yellow-900/20",
    ring: "ring-yellow-500",
  },
  down: {
    label: "Down",
    color: "text-red-700 dark:text-red-300",
    bg: "bg-red-50 dark:bg-red-900/20",
    ring: "ring-red-500",
  },
  unknown: {
    label: "Unknown",
    color: "text-gray-500",
    bg: "bg-gray-50 dark:bg-gray-800",
    ring: "ring-gray-400",
  },
};

function StatusIndicator({ status }: { status: string }) {
  const s = STATUS_STYLES[status] ?? STATUS_STYLES.unknown;
  return (
    <div className={`flex items-center gap-2 rounded-lg px-3 py-2 ${s.bg}`}>
      <span className={`h-3 w-3 rounded-full ring-2 ${s.ring} bg-current ${s.color}`} />
      <span className={`text-sm font-semibold ${s.color}`}>{s.label}</span>
    </div>
  );
}

function UptimeCard({ window: w, label }: { window: UptimeWindow; label: string }) {
  const color =
    w.uptime_pct >= 99.9
      ? "text-green-600"
      : w.uptime_pct >= 99.0
        ? "text-yellow-600"
        : "text-red-600";

  return (
    <div className="rounded-lg border border-gray-200 p-3 dark:border-gray-700">
      <p className="text-xs text-gray-500">{label}</p>
      <p className={`text-xl font-bold ${color}`}>{w.uptime_pct.toFixed(2)}%</p>
      <p className="text-[10px] text-gray-400">
        {w.successful_checks}/{w.total_checks} checks •{" "}
        {w.downtime_minutes > 0 ? `${w.downtime_minutes.toFixed(0)}min downtime` : "No downtime"}
      </p>
    </div>
  );
}

function SLACard({ sla }: { sla: SLACompliance }) {
  return (
    <div
      className={`rounded-lg border p-3 ${sla.compliant ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/10" : "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/10"}`}
    >
      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-500">SLA Target: {sla.target_pct}%</p>
        <span
          className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${sla.compliant ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300" : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300"}`}
        >
          {sla.compliant ? "✓ Compliant" : "✗ Breached"}
        </span>
      </div>
      <p className="mt-1 text-lg font-bold">{sla.actual_pct.toFixed(2)}%</p>
      <p className="text-[10px] text-gray-400">
        Budget: {sla.budget_remaining_minutes.toFixed(0)}min remaining
      </p>
    </div>
  );
}

function formatEventTime(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function AppHealthDashboard({ health }: AppHealthDashboardProps) {
  const lastHb = health.last_heartbeat_at ? formatEventTime(health.last_heartbeat_at) : "Never";

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">{health.app_name}</h2>
          <p className="text-xs text-gray-500">Last heartbeat: {lastHb}</p>
        </div>
        <StatusIndicator status={health.current_status} />
      </div>

      {health.consecutive_failures > 0 && (
        <div className="rounded-md bg-red-50 px-3 py-2 text-xs text-red-700 dark:bg-red-900/10 dark:text-red-400">
          ⚠ {health.consecutive_failures} consecutive probe failure
          {health.consecutive_failures !== 1 ? "s" : ""}
        </div>
      )}

      {/* Uptime cards */}
      <div className="grid grid-cols-3 gap-3">
        <UptimeCard window={health.uptime_24h} label="24 Hours" />
        <UptimeCard window={health.uptime_7d} label="7 Days" />
        <UptimeCard window={health.uptime_30d} label="30 Days" />
      </div>

      {/* SLA */}
      <SLACard sla={health.sla_compliance} />

      {/* Event timeline */}
      {health.recent_events.length > 0 && (
        <div>
          <h3 className="mb-2 text-xs font-semibold text-gray-500">Recent Events</h3>
          <div className="space-y-1">
            {health.recent_events.map((e, i) => {
              const s = STATUS_STYLES[e.status] ?? STATUS_STYLES.unknown;
              return (
                <div key={i} className="flex items-center gap-2 text-xs">
                  <span className={`h-2 w-2 rounded-full ${s.ring} bg-current ring-1 ${s.color}`} />
                  <span className="text-gray-400">{formatEventTime(e.timestamp)}</span>
                  <span className={`font-medium ${s.color}`}>{s.label}</span>
                  {e.reason && <span className="truncate text-gray-400">— {e.reason}</span>}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
