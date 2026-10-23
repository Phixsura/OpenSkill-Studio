"use client";

interface Phase { id: string; label: string; icon: string; status: string; statusIcon: string; }
interface DeploymentMonitorProps { appName: string; version: string; environment: string;
  phases: Phase[]; progress: number; overall: string; currentPhase: string | null; }

const overallColors: Record<string, string> = {
  in_progress: "text-blue-600", success: "text-green-600", failed: "text-red-600",
};

export function DeploymentMonitor({ appName, version, environment, phases, progress,
  overall, currentPhase }: DeploymentMonitorProps) {
  return (
    <div className="mx-auto max-w-lg space-y-4">
      <div className="text-center">
        <h2 className="text-lg font-bold">🚀 Deploying {appName}</h2>
        <p className="text-sm text-gray-400">v{version} → {environment}</p>
      </div>
      <div className="h-3 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full transition-all ${overall === "failed" ? "bg-red-500" : overall === "success" ? "bg-green-500" : "bg-blue-500 animate-pulse"}`}
          style={{ width: `${progress}%` }} />
      </div>
      <p className={`text-center text-sm font-medium ${overallColors[overall] ?? ""}`}>
        {overall === "in_progress" ? `Deploying... ${progress}%` : overall === "success" ? "✅ Deployed!" : "❌ Failed"}
      </p>
      <div className="flex justify-between">
        {phases.map(p => (
          <div key={p.id} className="flex flex-col items-center gap-1">
            <span className={`text-xl ${p.status === "running" ? "animate-pulse" : ""}`}>{p.statusIcon}</span>
            <span className={`text-xs ${p.id === currentPhase ? "font-bold text-blue-600" : "text-gray-400"}`}>{p.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
