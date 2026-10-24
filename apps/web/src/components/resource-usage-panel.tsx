"use client";

interface Resource { name: string; icon: string; value: number; display: string; status: string; }
interface ResourceUsagePanelProps { resources: Resource[]; overall: string; }

const statusBar: Record<string, string> = { ok: "bg-green-500", warning: "bg-yellow-500", critical: "bg-red-500" };

export function ResourceUsagePanel({ resources, overall }: ResourceUsagePanelProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">📊 Resource Usage</h3>
        <span className={`text-xs ${overall === "ok" ? "text-green-600" : "text-red-600"}`}>
          {overall === "ok" ? "✅ Normal" : "🚨 Alert"}
        </span>
      </div>
      <div className="space-y-2">
        {resources.map(r => (
          <div key={r.name} className="space-y-1">
            <div className="flex justify-between text-sm">
              <span>{r.icon} {r.name}</span>
              <span className="text-xs text-gray-400">{r.display}</span>
            </div>
            <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
              <div className={`h-full rounded-full ${statusBar[r.status] ?? "bg-gray-400"}`}
                style={{ width: `${Math.min(r.value, 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
