"use client";

interface Prerequisite { name: string; type: string; status: string; passed: boolean; required: boolean; }
interface DeployDepCheckerProps { service: string; prerequisites: Prerequisite[];
  canDeploy: boolean; passed: number; total: number; blocking: number; }

export function DeployDepChecker({ service, prerequisites, canDeploy, passed, total, blocking }: DeployDepCheckerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${canDeploy ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <h3 className="font-semibold text-sm">🔍 Deploy Check: {service}</h3>
        <span className={`text-xs ${canDeploy ? "text-green-600" : "text-red-500"}`}>
          {canDeploy ? "✅ Ready" : `🚫 ${blocking} blocking`} · {passed}/{total}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {prerequisites.map(p => (
          <div key={p.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span>{p.passed ? "✅" : "❌"}</span>
              <span>{p.name}</span>
              {p.required && !p.passed && <span className="text-red-400 text-[10px]">required</span>}
            </div>
            <span className="text-gray-400">{p.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
