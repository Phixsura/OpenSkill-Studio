"use client";
interface PodAutoscalePanelProps { currentPods: int; desiredPods: int; action: string;
  metricValue: number; target: number; minPods: number; maxPods: number; }
export function PodAutoscalePanel({ currentPods, desiredPods, action, metricValue, target, minPods, maxPods }: { currentPods: number; desiredPods: number; action: string; metricValue: number; target: number; minPods: number; maxPods: number }) {
  const ACTION_STYLE: Record<string, string> = { scale_up: "text-green-600", scale_down: "text-blue-500", no_change: "text-gray-400" };
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📈 Pod Autoscaler</h3>
        <span className={`text-xs font-bold ${ACTION_STYLE[action] ?? ""}`}>
          {action.replace("_", " ")} · {currentPods} → {desiredPods} pods
        </span>
      </div>
      <div className="grid grid-cols-4 gap-2 p-4 text-center text-xs">
        <div><span className="text-gray-400">Current</span><div className="font-bold text-lg">{currentPods}</div></div>
        <div><span className="text-gray-400">Desired</span><div className="font-bold text-lg">{desiredPods}</div></div>
        <div><span className="text-gray-400">Metric</span><div className="font-bold text-lg">{metricValue}/{target}</div></div>
        <div><span className="text-gray-400">Range</span><div className="font-bold text-lg">{minPods}-{maxPods}</div></div>
      </div>
    </div>
  );
}
