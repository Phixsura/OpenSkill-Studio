"use client";
interface DeployFreezePanelProps { frozen: boolean; reason: string; remainingHours: number;
  freezeHistory: number; }
export function DeployFreezePanel({ frozen, reason, remainingHours, freezeHistory }: DeployFreezePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-center ${frozen ? "bg-red-500 text-white" : "bg-green-500 text-white"}`}>
        <h3 className="font-bold">{frozen ? "🛑 DEPLOY FREEZE ACTIVE" : "✅ Deployments Allowed"}</h3>
        {frozen && <p className="text-sm opacity-80 mt-1">{reason} · {remainingHours}h remaining</p>}
      </div>
      <div className="p-3 text-xs text-gray-400 text-center">{freezeHistory} freeze(s) in history</div>
    </div>
  );
}
