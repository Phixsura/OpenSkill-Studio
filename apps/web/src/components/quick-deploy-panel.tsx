"use client";

interface DeployStep { name: string; status: string; icon: string; }
interface QuickDeployPanelProps { version: string; environment: string; status: string;
  steps: DeployStep[]; estimatedSeconds: number; onDeploy: () => void; }

const stepStatus: Record<string, string> = {
  running: "text-blue-600 animate-pulse", completed: "text-green-600", pending: "text-gray-400", failed: "text-red-600",
};

export function QuickDeployPanel({ version, environment, status, steps, estimatedSeconds, onDeploy }: QuickDeployPanelProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold">Quick Deploy</h3>
          <p className="text-xs text-gray-400">v{version} → {environment} · ~{estimatedSeconds}s</p>
        </div>
        <button onClick={onDeploy} disabled={status === "deploying"}
          className="rounded bg-green-600 px-4 py-2 text-sm text-white font-medium disabled:opacity-50">
          {status === "deploying" ? "Deploying..." : "🚀 Deploy"}
        </button>
      </div>
      <div className="space-y-2">
        {steps.map(s => (
          <div key={s.name} className="flex items-center gap-2">
            <span className={`text-sm ${stepStatus[s.status] ?? ""}`}>{s.status === "completed" ? "✓" : s.icon}</span>
            <span className={`text-sm ${s.status === "pending" ? "text-gray-400" : ""}`}>{s.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
