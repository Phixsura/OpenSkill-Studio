"use client";

interface PipelineStage { name: string; status: string; icon: string; duration_s: number; }
interface DeploymentPipelineProps { stages: PipelineStage[]; overall: string; totalDurationS: number; }

const statusStyles: Record<string, string> = {
  success: "bg-green-500", failed: "bg-red-500", running: "bg-blue-500 animate-pulse",
  pending: "bg-gray-300 dark:bg-gray-600",
};

export function DeploymentPipeline({ stages, overall, totalDurationS }: DeploymentPipelineProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Pipeline</h3>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span className={`h-2 w-2 rounded-full ${statusStyles[overall] ?? ""}`} />
          <span className="capitalize">{overall}</span>
          <span>· {totalDurationS}s</span>
        </div>
      </div>
      <div className="flex items-center gap-1">
        {stages.map((s, i) => (
          <div key={i} className="flex items-center gap-1">
            {i > 0 && <div className="h-px w-6 bg-gray-300 dark:bg-gray-600" />}
            <div className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium text-white ${statusStyles[s.status] ?? "bg-gray-400"}`}>
              <span>{s.icon}</span>
              <span>{s.name}</span>
              <span className="opacity-75">{s.duration_s}s</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
