"use client";

interface ScaleInfo { name: string; replicas: number; cpuPct: number; action: string; }
interface AutoscalerDashProps { services: ScaleInfo[]; totalReplicas: number; avgCpu: number; }

const ACTION_STYLE: Record<string, string> = {
  scale_up: "text-green-600", scale_down: "text-blue-500", no_change: "text-gray-400",
};

export function AutoscalerDash({ services, totalReplicas, avgCpu }: AutoscalerDashProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Autoscaler</h3>
        <span className="text-xs text-gray-400">{totalReplicas} replicas · {avgCpu}% avg CPU</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {services.map(s => (
          <div key={s.name} className="flex items-center justify-between px-4 py-2 text-xs">
            <div>
              <span className="font-mono">{s.name}</span>
              <span className="text-gray-400 ml-2">{s.replicas} pods · {s.cpuPct}%</span>
            </div>
            <span className={`font-bold ${ACTION_STYLE[s.action] ?? ""}`}>{s.action.replace("_", " ")}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
