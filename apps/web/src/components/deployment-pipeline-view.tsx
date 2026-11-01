"use client";

interface Stage { name: string; status: string; }
interface DeploymentPipelineViewProps { deploymentId: string; version: string; strategy: string;
  stages: Stage[]; status: string; onCancel: () => void; }

const stageIcon = (s: string) => s === "success" ? "✅" : s === "failed" ? "❌" : s === "in_progress" ? "⏳" : "⬜";
const statusColor = (s: string) => s === "completed" ? "text-green-600" : s === "failed" ? "text-red-600" : "text-blue-600";

export function DeploymentPipelineView({ deploymentId, version, strategy, stages, status, onCancel }: DeploymentPipelineViewProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Deployment</h2>
          <p className="text-xs text-gray-400">v{version} · {strategy} · {deploymentId}</p>
        </div>
        <span className={`text-sm font-bold ${statusColor(status)}`}>{status}</span>
      </div>
      <div className="flex items-center gap-1">
        {stages.map((s, i) => (
          <div key={s.name} className="flex flex-1 flex-col items-center">
            <span className="text-lg">{stageIcon(s.status)}</span>
            <span className="mt-0.5 text-xs capitalize">{s.name}</span>
            {i < stages.length - 1 && <div className="mt-1 h-0.5 w-full bg-gray-200 dark:bg-gray-700" />}
          </div>
        ))}
      </div>
      {status !== "completed" && status !== "failed" && (
        <button onClick={onCancel} className="w-full rounded border border-red-300 py-1.5 text-sm text-red-600">
          Cancel Deployment
        </button>
      )}
    </div>
  );
}
