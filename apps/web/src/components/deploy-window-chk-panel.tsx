"use client";
interface DeployWindowChkPanelProps { allowed: boolean; reason: string; windowName: string; remainingHours: number; }
export function DeployWindowChkPanel({ allowed, reason, windowName, remainingHours }: DeployWindowChkPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-white text-center ${allowed ? "bg-green-500" : "bg-red-500"}`}>
        <h3 className="font-bold">{allowed ? `✅ Deploy Allowed — ${windowName}` : `🛑 Deploy Blocked — ${reason.replace(/_/g, " ")}`}</h3>
        {allowed && <p className="text-xs opacity-80">{remainingHours}h remaining in window</p>}
      </div>
    </div>
  );
}
