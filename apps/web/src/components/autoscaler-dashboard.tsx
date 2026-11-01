"use client";

interface AutoscalerDashboardProps { name: string; current: number; desired: number;
  minReplicas: number; maxReplicas: number; currentCpu: number; targetCpu: number;
  action: string; scaleUps: number; scaleDowns: number; }

export function AutoscalerDashboard({ name, current, desired, minReplicas, maxReplicas, currentCpu, targetCpu, action, scaleUps, scaleDowns }: AutoscalerDashboardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Autoscaler: {name}</h3>
        <span className={`text-xs font-medium ${action === "scale_up" ? "text-red-500" : action === "scale_down" ? "text-blue-500" : "text-green-600"}`}>
          {action === "none" ? "✅ Stable" : action === "scale_up" ? "⬆ Scaling Up" : "⬇ Scaling Down"}
        </span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Current", v: current }, { l: "Desired", v: desired },
          { l: "CPU", v: `${currentCpu}%` }, { l: "Target", v: `${targetCpu}%` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      <div className="p-3 flex justify-between text-xs text-gray-400">
        <span>Range: {minReplicas}–{maxReplicas}</span>
        <span>↑{scaleUps} ↓{scaleDowns}</span>
      </div>
    </div>
  );
}
