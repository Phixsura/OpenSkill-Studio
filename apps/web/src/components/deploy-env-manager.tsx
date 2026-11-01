"use client";

interface Environment { name: string; tier: string; autoDeploy: boolean; approvalRequired: boolean; version?: string; }
interface DeployEnvManagerProps { environments: Environment[]; inSync: boolean;
  onDeploy: (env: string) => void; }

const TIER_COLORS: Record<string, string> = {
  dev: "bg-gray-100 text-gray-700", "non-prod": "bg-blue-100 text-blue-700",
  prod: "bg-red-100 text-red-700",
};

export function DeployEnvManager({ environments, inSync, onDeploy }: DeployEnvManagerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌍 Environments</h3>
        <span className={`text-xs ${inSync ? "text-green-600" : "text-yellow-600"}`}>
          {inSync ? "✅ In Sync" : "⚠ Out of Sync"}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {environments.map(e => (
          <div key={e.name} className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium capitalize">{e.name}</span>
              <span className={`px-1.5 py-0.5 text-[10px] rounded ${TIER_COLORS[e.tier] ?? ""}`}>{e.tier}</span>
              {e.version && <span className="text-xs font-mono text-gray-400">v{e.version}</span>}
            </div>
            <button onClick={() => onDeploy(e.name)}
              className="px-2 py-1 text-xs bg-blue-500 text-white rounded">
              {e.approvalRequired ? "🔐 Deploy" : "Deploy"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
