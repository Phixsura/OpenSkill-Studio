"use client";

interface PipelineStep { name: string; type: string; status: string; durationMs: number; records: number; error: string | null; }
interface PipelineMonitorProps { pipelineName: string; status: string; steps: PipelineStep[];
  totalRecords: number; durationDisplay: string; }

const STEP_ICON: Record<string, string> = { extract: "📥", transform: "🔄", load: "📤" };
const STATUS_COLOR: Record<string, string> = {
  completed: "bg-green-500", failed: "bg-red-500", running: "bg-blue-500", pending: "bg-gray-300 dark:bg-gray-600",
};

export function PipelineMonitor({ pipelineName, status, steps, totalRecords, durationDisplay }: PipelineMonitorProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔧 {pipelineName}</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{durationDisplay}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
            status === "completed" ? "bg-green-100 text-green-700" :
            status === "failed" ? "bg-red-100 text-red-700" :
            "bg-blue-100 text-blue-700"
          }`}>{status}</span>
        </div>
      </div>
      <div className="flex items-center gap-1 mb-4">
        {steps.map((s, i) => (
          <div key={s.name} className="flex items-center gap-1 flex-1">
            <div className={`h-2 flex-1 rounded-full ${STATUS_COLOR[s.status]}`} />
            {i < steps.length - 1 && <span className="text-gray-300 text-xs">→</span>}
          </div>
        ))}
      </div>
      <div className="space-y-2">
        {steps.map(s => (
          <div key={s.name} className="flex items-center justify-between text-sm">
            <span>{STEP_ICON[s.type] || "📌"} {s.name}</span>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>{s.records.toLocaleString()} records</span>
              <span>{s.durationMs}ms</span>
              {s.error && <span className="text-red-500">{s.error}</span>}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-3 text-xs text-gray-400 text-right">{totalRecords.toLocaleString()} total records processed</div>
    </div>
  );
}
