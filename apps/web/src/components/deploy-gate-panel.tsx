"use client";
interface Gate { name: string; passed: boolean; required: boolean; }
interface DeployGatePanelProps { gates: Gate[]; canDeploy: boolean; passed: number; total: number; }
export function DeployGatePanel({ gates, canDeploy, passed, total }: DeployGatePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚧 Deploy Gates</h3>
        <span className={`text-xs font-bold ${canDeploy ? "text-green-600" : "text-red-500"}`}>
          {canDeploy ? "✅ Ready" : "❌ Blocked"} · {passed}/{total}
        </span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {gates.map(g => (
          <div key={g.name} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span>{g.passed ? "✅" : "❌"}</span>
              <span className={!g.passed && g.required ? "text-red-600 font-bold" : ""}>{g.name}</span>
            </div>
            <span className="text-gray-400">{g.required ? "required" : "optional"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
