"use client";
interface SeverityClassPanelProps { severity: string; label: string; responseTime: string;
  affectedUsers: number; servicesDown: number; revenueImpact: number; dataLoss: boolean; }
const SEV_STYLE: Record<string, string> = { P1: "bg-red-600", P2: "bg-orange-500", P3: "bg-yellow-500", P4: "bg-blue-500" };
export function SeverityClassPanel({ severity, label, responseTime, affectedUsers, servicesDown, revenueImpact, dataLoss }: SeverityClassPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-4 text-white text-center ${SEV_STYLE[severity] ?? "bg-gray-500"}`}>
        <h3 className="font-black text-xl">{severity} — {label}</h3>
        <p className="text-sm opacity-80">Response: {responseTime}</p>
      </div>
      <div className="grid grid-cols-4 gap-2 p-4 text-center text-xs">
        <div><span className="text-gray-400">Users</span><div className="font-bold">{affectedUsers.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Services</span><div className="font-bold">{servicesDown}</div></div>
        <div><span className="text-gray-400">$/hr</span><div className="font-bold">${revenueImpact.toLocaleString()}</div></div>
        <div><span className="text-gray-400">Data Loss</span><div className={`font-bold ${dataLoss ? "text-red-500" : "text-green-600"}`}>{dataLoss ? "YES" : "No"}</div></div>
      </div>
    </div>
  );
}
