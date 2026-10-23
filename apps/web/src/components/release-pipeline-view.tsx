"use client";

interface PipelineStage { name: string; status: string; gate_type: string; reason?: string; }
interface ReleasePipelineViewProps { stages: PipelineStage[]; status: string; progressPct: number; }

const STAGE_ICONS: Record<string, string> = { passed: "✅", failed: "❌", pending: "⏳", running: "🔄" };
const STAGE_COLORS: Record<string, string> = { passed: "border-green-500", failed: "border-red-500", pending: "border-gray-300", running: "border-blue-500" };

export function ReleasePipelineView({ stages, status, progressPct }: ReleasePipelineViewProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Release Pipeline</h3>
        <span className={`text-xs font-medium ${status === "completed" ? "text-green-600" : status === "blocked" ? "text-red-600" : "text-blue-600"}`}>{status}</span>
      </div>
      <div className="mt-2 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full ${status === "blocked" ? "bg-red-500" : "bg-blue-600"}`} style={{ width: `${progressPct}%` }} />
      </div>
      <div className="mt-4 flex gap-2">
        {stages.map((s, i) => (
          <div key={i} className={`flex-1 rounded-lg border-2 p-2 text-center ${STAGE_COLORS[s.status] || "border-gray-300"}`}>
            <span className="text-lg">{STAGE_ICONS[s.status] || "⏳"}</span>
            <p className="mt-1 text-xs font-medium">{s.name}</p>
            {s.reason && <p className="text-xs text-red-500">{s.reason}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
