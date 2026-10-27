"use client";

interface Stage { name: string; status: string; output: string; }
interface Pipeline { pipelineId: string; version: string; trigger: string; status: string; stages: Stage[]; }

const stageIcons: Record<string, string> = { pending: "⬜", running: "🔄", passed: "✅", failed: "❌", skipped: "⏭️" };
const statusColors: Record<string, string> = { passed: "text-green-600", failed: "text-red-600", running: "text-blue-600", pending: "text-gray-400" };

export function PipelineStatus({ pipeline }: { pipeline: Pipeline }) {
  return (
    <div className="border dark:border-gray-700 rounded-xl p-4 space-y-3">
      <div className="flex justify-between items-center">
        <div>
          <span className="font-bold text-sm">v{pipeline.version}</span>
          <span className="text-xs text-gray-500 ml-2">via {pipeline.trigger}</span>
        </div>
        <span className={`text-xs font-medium capitalize ${statusColors[pipeline.status] || ""}`}>{pipeline.status}</span>
      </div>
      <div className="flex items-center gap-1">
        {pipeline.stages.map((s, i) => (
          <div key={s.name} className="flex items-center">
            <div className="text-center">
              <span className="text-lg block">{stageIcons[s.status] || "⬜"}</span>
              <span className="text-[10px] text-gray-500">{s.name}</span>
            </div>
            {i < pipeline.stages.length - 1 && <div className="w-6 h-px bg-gray-300 dark:bg-gray-600 mx-0.5" />}
          </div>
        ))}
      </div>
      {pipeline.stages.some(s => s.output) && (
        <div className="text-xs bg-gray-50 dark:bg-gray-800 rounded-lg p-2 font-mono">
          {pipeline.stages.filter(s => s.output).map(s => (
            <div key={s.name}><span className="text-gray-400">[{s.name}]</span> {s.output}</div>
          ))}
        </div>
      )}
    </div>
  );
}
