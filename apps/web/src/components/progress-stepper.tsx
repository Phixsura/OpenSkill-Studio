"use client";

interface Step { index: number; name: string; status: string; description: string; }
interface ProgressStepperProps { title: string; steps: Step[]; progressPct: number; currentStep: number | null; }

const stepIcon = (s: string) => s === "completed" ? "✅" : s === "in_progress" ? "🔵" : "⬜";

export function ProgressStepper({ title, steps, progressPct, currentStep }: ProgressStepperProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{title}</h2>
        <span className="text-sm font-bold">{progressPct}%</span>
      </div>
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="space-y-2">
        {steps.map(s => (
          <div key={s.index} className={`flex items-start gap-3 rounded-lg border p-3 ${s.status === "in_progress" ? "border-blue-300 bg-blue-50 dark:border-blue-700 dark:bg-blue-900/10" : "dark:border-gray-700"}`}>
            <span className="text-lg">{stepIcon(s.status)}</span>
            <div>
              <p className={`text-sm ${s.status === "completed" ? "text-gray-400 line-through" : "font-medium"}`}>{s.name}</p>
              {s.description && <p className="text-xs text-gray-400">{s.description}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
