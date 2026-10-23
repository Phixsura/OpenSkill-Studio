"use client";

interface PipelineStage { index: number; name: string; type: string;
  environment: string; approvalRequired: boolean; status: string; }
interface DeployPipelineBuilderProps { name: string; stages: PipelineStage[];
  progressPct: number; blocked: boolean; onApprove: (index: number) => void; }

const STAGE_ICON: Record<string, string> = { build: "🔨", test: "🧪", deploy: "🚀", gate: "🚦" };
const STATUS_COLOR: Record<string, string> = {
  completed: "bg-green-500", pending: "bg-gray-300 dark:bg-gray-600",
  awaiting_approval: "bg-yellow-500",
};

export function DeployPipelineBuilder({ name, stages, progressPct, blocked, onApprove }: DeployPipelineBuilderProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">🔧 {name}</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">{progressPct}%</span>
          {blocked && <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700">Awaiting Approval</span>}
        </div>
      </div>
      <div className="flex items-center gap-1 mb-4">
        {stages.map((s, i) => (
          <div key={s.index} className="flex items-center flex-1">
            <div className={`w-full h-2 rounded-full ${STATUS_COLOR[s.status] || "bg-gray-300"}`} />
            {i < stages.length - 1 && <span className="text-gray-300 mx-0.5">›</span>}
          </div>
        ))}
      </div>
      <div className="space-y-2">
        {stages.map(s => (
          <div key={s.index} className="flex items-center justify-between text-sm bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
            <div className="flex items-center gap-2">
              <span>{STAGE_ICON[s.type] || "📌"}</span>
              <span className="font-medium">{s.name}</span>
              <span className="text-xs text-gray-400">{s.environment}</span>
            </div>
            {s.status === "awaiting_approval" ? (
              <button onClick={() => onApprove(s.index)}
                className="text-xs px-2 py-1 bg-green-600 text-white rounded hover:bg-green-700">Approve</button>
            ) : (
              <span className={`text-xs ${s.status === "completed" ? "text-green-600" : "text-gray-400"}`}>{s.status}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
