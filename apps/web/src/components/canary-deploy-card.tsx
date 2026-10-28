"use client";

interface StageInfo {
  stage_id: string;
  traffic_pct: number;
  duration_seconds: number;
  healthy: boolean | null;
}

interface DeployInfo {
  deploy_id: string;
  version: string;
  stages: StageInfo[];
  current_stage: number;
  status: "pending" | "in_progress" | "completed" | "rolled_back";
}

interface CanaryDeployCardProps {
  deploys: DeployInfo[];
  appName: string;
}

const statusColors: Record<string, string> = {
  pending: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  in_progress: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  completed: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  rolled_back: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function CanaryDeployCard({ deploys, appName }: CanaryDeployCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🐤 Canary Deploys
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{deploys.length} deploys</span>
      </div>

      {deploys.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No canary deploys</p>
      ) : (
        <div className="space-y-3">
          {deploys.map((d) => (
            <div
              key={d.deploy_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  {d.version}
                </span>
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusColors[d.status] ?? ""}`}
                >
                  {d.status.replace("_", " ")}
                </span>
              </div>
              <div className="mt-1.5 flex gap-1">
                {d.stages.map((s, i) => (
                  <div
                    key={s.stage_id}
                    className={`flex-1 rounded-sm px-1 py-0.5 text-center text-[9px] ${
                      i < d.current_stage
                        ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                        : i === d.current_stage && d.status === "in_progress"
                          ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300"
                          : "bg-gray-50 text-gray-400 dark:bg-gray-800"
                    }`}
                  >
                    {s.traffic_pct}%
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
