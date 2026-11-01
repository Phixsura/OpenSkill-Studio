"use client";

interface BuildStage {
  name: string;
  status: "queued" | "running" | "passed" | "failed" | "cancelled";
  durationMs: number;
  log?: string;
}

interface BuildRun {
  buildId: string;
  version: string;
  trigger: string;
  status: "queued" | "running" | "passed" | "failed" | "cancelled";
  stages: BuildStage[];
  artifactUrl?: string;
}

const stageConfig: Record<string, { color: string; icon: string }> = {
  queued: { color: "bg-gray-300 dark:bg-gray-600", icon: "⏳" },
  running: { color: "bg-blue-500 animate-pulse", icon: "▶" },
  passed: { color: "bg-green-500", icon: "✅" },
  failed: { color: "bg-red-500", icon: "❌" },
  cancelled: { color: "bg-gray-400", icon: "⊘" },
};

export function BuildPipelinePanel({
  builds,
  onCancel,
  onRetrigger,
}: {
  builds: BuildRun[];
  onCancel?: (buildId: string) => void;
  onRetrigger?: (buildId: string) => void;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🏗️ Build Pipeline</h2>

      <div className="space-y-3">
        {builds.map((build) => {
          const cfg = stageConfig[build.status];
          return (
            <div key={build.buildId} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span>{cfg.icon}</span>
                  <span className="font-semibold text-sm">v{build.version}</span>
                  <span className="text-xs text-gray-400">{build.trigger}</span>
                  <span className={`text-xs text-white px-1.5 py-0.5 rounded ${stageConfig[build.status].color.split(" ")[0]}`}>
                    {build.status}
                  </span>
                </div>
                <div className="flex gap-1">
                  {build.status === "running" && (
                    <button onClick={() => onCancel?.(build.buildId)}
                      className="text-xs bg-red-600 text-white px-2 py-1 rounded">Cancel</button>
                  )}
                  {build.status === "failed" && (
                    <button onClick={() => onRetrigger?.(build.buildId)}
                      className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Retry</button>
                  )}
                </div>
              </div>

              {/* Stage pipeline visualization */}
              <div className="flex gap-0.5">
                {build.stages.map((stage, i) => {
                  const sCfg = stageConfig[stage.status];
                  return (
                    <div key={i} className="flex-1 group relative">
                      <div className={`h-6 rounded ${sCfg.color} flex items-center justify-center`}>
                        <span className="text-[10px] text-white font-medium">{stage.name}</span>
                      </div>
                      {stage.durationMs > 0 && (
                        <span className="text-[9px] text-gray-400 block text-center mt-0.5">
                          {stage.durationMs > 1000 ? `${(stage.durationMs / 1000).toFixed(1)}s` : `${stage.durationMs}ms`}
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>

              {build.artifactUrl && (
                <div className="text-xs text-blue-500 mt-2">📦 {build.artifactUrl}</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
