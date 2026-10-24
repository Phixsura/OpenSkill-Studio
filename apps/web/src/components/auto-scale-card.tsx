"use client";

interface AutoScaleCardProps { name: string; metric: string; targetValue: number;
  currentReplicas: number; desiredReplicas: number; action: string;
  minReplicas: number; maxReplicas: number; }

export function AutoScaleCard({ name, metric, targetValue, currentReplicas, desiredReplicas, action, minReplicas, maxReplicas }: AutoScaleCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">📈 {name}</h3>
        <span className={`text-xs font-medium ${action === "scale_up" ? "text-red-500" : action === "scale_down" ? "text-blue-500" : "text-green-600"}`}>
          {action === "none" ? "✅ Stable" : action === "scale_up" ? "⬆ Scaling Up" : "⬇ Scaling Down"}
        </span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Current", v: currentReplicas }, { l: "Desired", v: desiredReplicas },
          { l: "Target", v: `${targetValue}%` }, { l: "Range", v: `${minReplicas}-${maxReplicas}` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className="text-sm font-bold">{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
