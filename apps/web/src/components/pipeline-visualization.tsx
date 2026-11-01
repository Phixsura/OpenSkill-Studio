"use client";

interface PipelineStage { name: string; status: string; durationMs: number; }
interface PipelineVisualizationProps { name: string; commit: string;
  stages: PipelineStage[]; status: string; progressPct: number; }

const STAGE_COLORS: Record<string, { bg: string; text: string }> = {
  passed: { bg: "bg-green-500", text: "text-white" },
  failed: { bg: "bg-red-500", text: "text-white" },
  running: { bg: "bg-blue-500", text: "text-white" },
  pending: { bg: "bg-gray-200 dark:bg-gray-700", text: "text-gray-400" },
};

export function PipelineVisualization({ name, commit, stages, status, progressPct }: PipelineVisualizationProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <div>
          <h3 className="font-semibold text-sm">🔄 {name}</h3>
          <div className="text-[10px] text-gray-400 font-mono">{commit}</div>
        </div>
        <div className="text-right">
          <span className={`text-xs font-medium ${status === "completed" ? "text-green-600" : status === "failed" ? "text-red-500" : "text-blue-500"}`}>
            {status} · {progressPct}%
          </span>
        </div>
      </div>
      <div className="flex items-center gap-1 p-4">
        {stages.map((s, i) => {
          const c = STAGE_COLORS[s.status] ?? STAGE_COLORS.pending;
          return (
            <div key={s.name} className="flex items-center flex-1">
              <div className={`flex-1 rounded-lg p-2 text-center text-[10px] ${c.bg} ${c.text}`}>
                <div className="font-medium">{s.name.replaceAll("_", " ")}</div>
                {s.durationMs > 0 && <div>{(s.durationMs / 1000).toFixed(1)}s</div>}
              </div>
              {i < stages.length - 1 && <span className="text-gray-300 mx-0.5">→</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
