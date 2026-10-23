"use client";

interface Step { index: number; label: string; status: string; icon: string; }
interface ProgressStepperProps { steps: Step[]; progressPct: number; }

const statusStyle: Record<string, string> = {
  completed: "bg-green-500 text-white",
  current: "bg-blue-600 text-white ring-2 ring-blue-300",
  pending: "bg-gray-200 text-gray-500 dark:bg-gray-700",
};

export function ProgressStepper({ steps, progressPct }: ProgressStepperProps) {
  return (
    <div className="space-y-4">
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="flex justify-between">
        {steps.map(s => (
          <div key={s.index} className="flex flex-col items-center gap-1">
            <div className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium ${statusStyle[s.status]}`}>
              {s.icon}
            </div>
            <span className={`text-xs ${s.status === "current" ? "font-medium" : "text-gray-400"}`}>{s.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
