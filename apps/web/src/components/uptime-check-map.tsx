"use client";

interface RegionCheck { region: string; status: string; latency_ms: number; status_code: number; }
interface UptimeCheckMapProps { endpoint: string; checks: RegionCheck[]; avgLatencyMs: number; status: string; }

const regionLabels: Record<string, string> = {
  "us-east": "🇺🇸 US East", "us-west": "🇺🇸 US West",
  "eu-west": "🇪🇺 Europe", "ap-east": "🇯🇵 Asia Pacific",
};

export function UptimeCheckMap({ endpoint, checks, avgLatencyMs, status }: UptimeCheckMapProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Uptime Checks</h2>
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${status === "operational" ? "bg-green-500" : "bg-red-500"}`} />
          <span className="text-sm">{avgLatencyMs}ms avg</span>
        </div>
      </div>
      <p className="truncate font-mono text-xs text-gray-400">{endpoint}</p>
      <div className="grid grid-cols-2 gap-2">
        {checks.map(c => (
          <div key={c.region} className={`rounded-lg border p-3 ${c.status === "up" ? "border-green-200 dark:border-green-800" : "border-red-200 dark:border-red-800"}`}>
            <p className="text-sm font-medium">{regionLabels[c.region] ?? c.region}</p>
            <div className="mt-1 flex items-center justify-between text-xs">
              <span className={c.status === "up" ? "text-green-600" : "text-red-600"}>
                {c.status === "up" ? "✅" : "❌"} {c.status_code}
              </span>
              <span className="text-gray-400">{c.latency_ms}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
