"use client";

interface StageInfo {
  stage_id: string;
  name: string;
  stage_type: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  duration_ms: number | null;
  input_count: number;
  output_count: number;
  error: string | null;
}

interface DataPipelineCardProps {
  pipelineId: string;
  pipelineName: string;
  stages: StageInfo[];
  status: string;
  appName: string;
}

const STAGE_ICONS: Record<string, string> = {
  pending: "○",
  running: "◉",
  completed: "●",
  failed: "✕",
  skipped: "⊘",
};

const STAGE_COLORS: Record<string, string> = {
  pending: "text-gray-400",
  running: "text-blue-600 dark:text-blue-400",
  completed: "text-green-600 dark:text-green-400",
  failed: "text-red-600 dark:text-red-400",
  skipped: "text-gray-300 dark:text-gray-600",
};

export default function DataPipelineCard({
  pipelineId,
  pipelineName,
  stages,
  status,
  appName,
}: DataPipelineCardProps) {
  const completedStages = stages.filter((s) => s.status === "completed").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">{pipelineName}</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {appName} · {pipelineId}
          </p>
        </div>
        <span className="text-xs text-gray-400">
          {completedStages}/{stages.length} stages
        </span>
      </div>

      <div className="space-y-2">
        {stages.map((s, i) => {
          const icon = STAGE_ICONS[s.status] ?? "○";
          const color = STAGE_COLORS[s.status] ?? "text-gray-400";
          return (
            <div key={s.stage_id} className="flex items-start gap-3">
              <div className="flex flex-col items-center">
                <span className={`text-sm ${color}`}>{icon}</span>
                {i < stages.length - 1 && (
                  <div
                    className={`h-4 w-px ${s.status === "completed" ? "bg-green-300" : "bg-gray-200 dark:bg-gray-700"}`}
                  />
                )}
              </div>
              <div className="min-w-0 flex-1 pb-1">
                <div className="flex items-center justify-between">
                  <span
                    className={`text-sm ${s.status === "skipped" ? "text-gray-400 line-through" : "text-gray-800 dark:text-gray-200"}`}
                  >
                    {s.name}
                  </span>
                  <div className="flex items-center gap-2 text-[11px] text-gray-400">
                    {s.duration_ms !== null && <span>{(s.duration_ms / 1000).toFixed(1)}s</span>}
                    {s.output_count > 0 && <span>{s.output_count} out</span>}
                  </div>
                </div>
                {s.error && <p className="text-[11px] text-red-500">{s.error}</p>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
