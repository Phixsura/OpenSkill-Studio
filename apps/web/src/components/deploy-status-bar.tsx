"use client";

interface EnvDeploy { environment: string; icon: string; version: string; status: string; deployedAt: string; deployer: string; commit: string; }
interface DeployStatusBarProps { environments: EnvDeploy[]; versionsInSync: boolean; }

export function DeployStatusBar({ environments, versionsInSync }: DeployStatusBarProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Deploy Status</h3>
        <span className={`text-xs ${versionsInSync ? "text-green-600" : "text-yellow-600"}`}>
          {versionsInSync ? "✓ All in sync" : "⚠ Version mismatch"}
        </span>
      </div>
      <div className="flex gap-2">
        {environments.map(e => (
          <div key={e.environment} className="flex-1 rounded-lg border p-3 dark:border-gray-700">
            <div className="flex items-center gap-1.5 mb-1">
              <span>{e.icon}</span>
              <span className="text-xs font-semibold capitalize">{e.environment}</span>
            </div>
            <p className="text-sm font-bold">v{e.version}</p>
            <p className="text-xs text-gray-400">{e.commit} · {e.deployer || "auto"}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
