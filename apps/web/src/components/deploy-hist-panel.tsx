"use client";
interface Deploy { version: string; env: string; deployer: string; status: string; }
interface DeployHistPanelProps { deploys: Deploy[]; successRate: number; }
export function DeployHistPanel({ deploys, successRate }: DeployHistPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📜 Deploy History</h3>
        <span className="text-xs text-gray-400">{deploys.length} deploys · {successRate}% success</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {deploys.map((d, i) => (
          <div key={i} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono">{d.version} → {d.env}</span>
            <span className={d.status === "success" ? "text-green-600" : "text-red-500"}>{d.status} by {d.deployer}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
