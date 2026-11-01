"use client";

interface HealthCheck {
  status: "healthy" | "degraded" | "down";
  version: string;
  build: string;
  uptimeSeconds: number;
  components: Record<string, { status: string; latencyMs: number; message: string }>;
}

const statusConfig: Record<string, { bg: string; icon: string; text: string }> = {
  healthy: { bg: "bg-green-500", icon: "✅", text: "All Systems Operational" },
  degraded: { bg: "bg-yellow-500", icon: "⚠️", text: "Partial Degradation" },
  down: { bg: "bg-red-500", icon: "🔴", text: "System Outage" },
};

function formatUptime(s: number) {
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  return d > 0 ? `${d}d ${h}h` : `${h}h ${Math.floor((s % 3600) / 60)}m`;
}

export function HealthCheckWidget({ health }: { health: HealthCheck }) {
  const cfg = statusConfig[health.status] || statusConfig.down;
  const components = Object.entries(health.components);

  return (
    <div className="space-y-3">
      <div className={`${cfg.bg} rounded-xl p-4 text-white text-center`}>
        <span className="text-2xl block">{cfg.icon}</span>
        <span className="font-bold block mt-1">{cfg.text}</span>
        <span className="text-xs opacity-80">v{health.version} · build {health.build} · up {formatUptime(health.uptimeSeconds)}</span>
      </div>

      <div className="space-y-0.5">
        {components.map(([name, comp]) => (
          <div key={name} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span className={`w-2.5 h-2.5 rounded-full ${comp.status === "healthy" ? "bg-green-500" : comp.status === "degraded" ? "bg-yellow-500" : "bg-red-500"}`} />
              <span>{name}</span>
            </div>
            <div className="flex gap-2 text-xs text-gray-400">
              {comp.latencyMs > 0 && <span>{comp.latencyMs}ms</span>}
              {comp.message && <span className="text-yellow-600">{comp.message}</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
