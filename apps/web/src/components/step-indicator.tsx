"use client";

interface Step { index: number; label: string; status: string; }
interface StepIndicatorProps { steps: Step[]; progressPct: number; }

export function StepIndicator({ steps, progressPct }: StepIndicatorProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        {steps.map((s, i) => (
          <div key={s.index} className="flex flex-1 items-center">
            <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
              s.status === "completed" ? "bg-green-500 text-white" :
              s.status === "current" ? "bg-blue-600 text-white" :
              "border-2 border-gray-300 text-gray-400 dark:border-gray-600"}`}>
              {s.status === "completed" ? "✓" : s.index + 1}
            </div>
            {i < steps.length - 1 && (
              <div className={`mx-2 h-0.5 flex-1 ${s.status === "completed" ? "bg-green-500" : "bg-gray-200 dark:bg-gray-700"}`} />
            )}
          </div>
        ))}
      </div>
      <div className="flex justify-between">
        {steps.map(s => (
          <span key={s.index} className={`text-xs ${s.status === "current" ? "font-medium" : "text-gray-400"}`}>
            {s.label}
          </span>
        ))}
      </div>
    </div>
  );
}
