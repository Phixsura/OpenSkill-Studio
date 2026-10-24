"use client";

interface StageResult { name: string; status: string; durationMs: number; error?: string; }
interface PipelineStageViewerProps { stages: StageResult[]; totalMs: number; passed: number; failed: boolean; }

const STATUS_STYLE: Record<string, string> = {
  success: "text-green-600", failed: "text-red-600", skipped: "text-gray-400",
};
const STATUS_ICON: Record<string, string> = {
  success: "✅", failed: "❌", skipped: "⏭️",
};

export function PipelineStageViewer({ stages, totalMs, passed, failed }: PipelineStageViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚡ Pipeline Stages</h3>
        <span className={`text-xs ${failed ? "text-red-500" : "text-green-600"}`}>
          {passed}/{stages.length} passed · {totalMs}ms
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {stages.map(s => (
          <div key={s.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span>{STATUS_ICON[s.status] ?? "⏳"}</span>
              <span className={STATUS_STYLE[s.status] ?? ""}>{s.name}</span>
            </div>
            <span className="text-gray-400">{s.durationMs}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
