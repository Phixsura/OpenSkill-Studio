"use client";

interface Step { id: string; label: string; required: boolean; completed: boolean; }
interface OnboardingChecklistCardProps { steps: Step[]; progressPct: number; onStepClick: (id: string) => void; }

export function OnboardingChecklistCard({ steps, progressPct, onStepClick }: OnboardingChecklistCardProps) {
  return (
    <div className="rounded-lg border border-blue-200 bg-blue-50/50 p-5 dark:border-blue-800 dark:bg-blue-900/10">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold">Getting Started</h2>
        <span className="text-sm text-blue-600 dark:text-blue-400">{progressPct}% complete</span>
      </div>
      <div className="mt-2 h-2 rounded-full bg-blue-100 dark:bg-blue-900/30">
        <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      <ul className="mt-4 space-y-2">
        {steps.map(s => (
          <li key={s.id}>
            <button onClick={() => onStepClick(s.id)}
              className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-left text-sm hover:bg-blue-100/50 dark:hover:bg-blue-900/20">
              <span className={`flex h-5 w-5 items-center justify-center rounded-full text-xs ${s.completed ? "bg-green-500 text-white" : "border border-gray-300 dark:border-gray-600"}`}>
                {s.completed ? "✓" : ""}
              </span>
              <span className={s.completed ? "text-gray-400 line-through" : ""}>{s.label}</span>
              {s.required && !s.completed && <span className="text-xs text-red-400">Required</span>}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
