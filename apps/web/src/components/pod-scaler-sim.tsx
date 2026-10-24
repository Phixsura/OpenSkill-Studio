"use client";

interface PodScalerSimProps { currentPods: number; desiredPods: number;
  currentCpu: number; targetCpu: number; action: string;
  atMin: boolean; atMax: boolean; minPods: number; maxPods: number; }

export function PodScalerSim({ currentPods, desiredPods, currentCpu, targetCpu, action, atMin, atMax, minPods, maxPods }: PodScalerSimProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔧 Pod Autoscaler</h3>
        <span className={`text-xs font-medium ${action === "scale_up" ? "text-red-500" : action === "scale_down" ? "text-blue-500" : "text-green-600"}`}>
          {action === "stable" ? "✅ Stable" : action === "scale_up" ? "⬆ Scaling Up" : "⬇ Scaling Down"}
        </span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Current", v: `${currentPods} pods` }, { l: "Desired", v: `${desiredPods} pods` },
          { l: "CPU", v: `${currentCpu}%` }, { l: "Target", v: `${targetCpu}%` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
      <div className="p-3 text-xs text-gray-400 flex justify-between">
        <span>Range: {minPods}–{maxPods}</span>
        {atMin && <span className="text-yellow-600">At minimum</span>}
        {atMax && <span className="text-red-500">At maximum</span>}
      </div>
    </div>
  );
}
