"use client";
interface DeployCadencePanelProps { totalDeploys: number; deploysPerDay: number; level: string;
  label: string; peakDay: string; peakCount: number; servicesDeployed: number; }
const LVL_COLOR: Record<string, string> = { elite: "text-green-600", high: "text-blue-500", medium: "text-yellow-600", low: "text-red-500" };
export function DeployCadencePanel({ totalDeploys, deploysPerDay, level, label, peakDay, peakCount, servicesDeployed }: DeployCadencePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚀 Deploy Cadence</h3>
        <span className={`text-xs font-bold ${LVL_COLOR[level] ?? ""}`}>{label} · {deploysPerDay}/day</span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Total</span><div className="font-bold text-lg">{totalDeploys}</div></div>
        <div><span className="text-gray-400">Peak</span><div className="font-bold text-lg">{peakCount}</div><div className="text-[10px] text-gray-400">{peakDay}</div></div>
        <div><span className="text-gray-400">Services</span><div className="font-bold text-lg">{servicesDeployed}</div></div>
      </div>
    </div>
  );
}
