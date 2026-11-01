"use client";
interface EnvStatus { env: string; success: number; failed: number; inProgress: number; total: number; }
interface DeployStatusPanelProps { envs: EnvStatus[]; allSuccess: boolean; perDay: number; successRate: number; }
export function DeployStatusPanel({ envs, allSuccess, perDay, successRate }: DeployStatusPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚀 Deploy Status</h3>
        <span className={`text-xs font-bold ${allSuccess ? "text-green-600" : "text-yellow-600"}`}>
          {perDay}/day · {successRate}% success
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {envs.map(e => (
          <div key={e.env} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-bold uppercase">{e.env}</span>
            <span className="text-gray-400">
              ✅{e.success} {e.failed > 0 ? `❌${e.failed} ` : ""}{e.inProgress > 0 ? `⏳${e.inProgress}` : ""}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
