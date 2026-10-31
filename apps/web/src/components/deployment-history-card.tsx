"use client";

interface DeploymentInfo {
  deploy_id: string;
  version: string;
  commit_sha: string;
  deployer: string;
  result: "success" | "failure" | "rollback" | "in_progress";
  duration_seconds: number | null;
}

interface DeploymentHistoryCardProps {
  deployments: DeploymentInfo[];
  successRate: number;
  appName: string;
}

const resultStyle: Record<string, string> = {
  success: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  failure: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  rollback: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  in_progress: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
};

export default function DeploymentHistoryCard({
  deployments,
  successRate,
  appName,
}: DeploymentHistoryCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            🚀 Deployment History
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{deployments.length} deploys</span>
          <p className="text-[10px] text-gray-500">{successRate}% success</p>
        </div>
      </div>

      {deployments.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No deployments</p>
      ) : (
        <div className="space-y-1.5">
          {deployments.map((d) => (
            <div
              key={d.deploy_id}
              className="rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-gray-800 dark:text-gray-200">
                    {d.version}
                  </span>
                  <span className="font-mono text-[10px] text-gray-400">
                    {d.commit_sha.slice(0, 7)}
                  </span>
                </div>
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${resultStyle[d.result]}`}
                >
                  {d.result.replace("_", " ")}
                </span>
              </div>
              <div className="mt-0.5 flex justify-between text-[10px] text-gray-400">
                <span>{d.deployer}</span>
                {d.duration_seconds !== null && <span>{d.duration_seconds}s</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
