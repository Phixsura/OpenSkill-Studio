"use client";

interface AutoscalerGaugeProps { currentReplicas: number; targetReplicas: number;
  action: string; currentCpuPct: number; targetCpuPct: number; min: number; max: number; }

export function AutoscalerGauge({ currentReplicas, targetReplicas, action,
  currentCpuPct, targetCpuPct, min, max }: AutoscalerGaugeProps) {
  const actionStyle = action === "scale_up" ? "text-red-600" :
                      action === "scale_down" ? "text-blue-600" : "text-green-600";
  const actionIcon = action === "scale_up" ? "⬆️" : action === "scale_down" ? "⬇️" :
                     action === "cooldown" ? "⏳" : "✅";
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">📈 Autoscaler</h3>
        <span className={`text-sm font-medium ${actionStyle}`}>{actionIcon} {action.replace("_", " ")}</span>
      </div>
      <div className="grid grid-cols-2 gap-4 text-center mb-4">
        <div>
          <p className="text-3xl font-bold">{currentReplicas}</p>
          <p className="text-xs text-gray-400">Current Pods</p>
        </div>
        <div>
          <p className="text-3xl font-bold">{targetReplicas}</p>
          <p className="text-xs text-gray-400">Target Pods</p>
        </div>
      </div>
      <div className="mb-2">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>CPU: {currentCpuPct}%</span><span>Target: {targetCpuPct}%</span>
        </div>
        <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
          <div className={`h-full rounded-full ${currentCpuPct > targetCpuPct ? "bg-red-500" : "bg-green-500"}`}
               style={{ width: `${Math.min(currentCpuPct, 100)}%` }} />
        </div>
      </div>
      <p className="text-xs text-gray-400 text-center">Range: {min}–{max} pods</p>
    </div>
  );
}
