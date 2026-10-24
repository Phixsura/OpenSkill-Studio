"use client";

interface PipelineStage { name: string; records: number; errors: number; throughputRps: number; }
interface PipelineMonitorDashProps { pipeline: string; stages: PipelineStage[];
  totalRecords: number; totalErrors: number; healthy: boolean; bottleneck: string | null; }

export function PipelineMonitorDash({ pipeline, stages, totalRecords, totalErrors, healthy, bottleneck }: PipelineMonitorDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">🔄 {pipeline}</h3>
        <div className="flex gap-2 text-xs">
          <span className={healthy ? "text-green-600" : "text-red-500"}>{healthy ? "✅ Healthy" : "⚠ Errors"}</span>
          {bottleneck && <span className="text-yellow-600">bottleneck: {bottleneck}</span>}
        </div>
      </div>
      <div className="flex items-center gap-1 p-3">
        {stages.map((s, i) => (
          <div key={s.name} className="flex items-center flex-1">
            <div className={`flex-1 p-2 rounded text-center text-[10px] border ${s.errors > 0 ? "border-red-300 bg-red-50 dark:bg-red-900/10" : "border-green-300 bg-green-50 dark:bg-green-900/10"}`}>
              <div className="font-medium">{s.name}</div>
              <div>{s.records.toLocaleString()} rec</div>
              <div>{s.throughputRps} rps</div>
            </div>
            {i < stages.length - 1 && <span className="text-gray-300 mx-0.5">→</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
