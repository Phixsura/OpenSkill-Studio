"use client";

interface Step { key: string; title: string; required: boolean; completed: boolean; }

interface OnboardingChecklistProps { steps: Step[]; progressPct: number; canPublish: boolean; }

export function OnboardingChecklist({ steps, progressPct, canPublish }: OnboardingChecklistProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-6 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Getting Started</h3>
        <span className="text-sm text-gray-500">{progressPct}% complete</span>
      </div>
      <div className="mt-2 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      {canPublish && (
        <div className="mt-3 rounded bg-green-50 px-3 py-2 text-sm text-green-700 dark:bg-green-900/20 dark:text-green-300">
          ✅ You can now publish apps!
        </div>
      )}
      <ul className="mt-4 space-y-2">
        {steps.map(s => (
          <li key={s.key} className="flex items-center gap-3 text-sm">
            <span className={s.completed ? "text-green-500" : "text-gray-300"}>{s.completed ? "✅" : "⬜"}</span>
            <span className={s.completed ? "line-through opacity-60" : ""}>{s.title}</span>
            {s.required && !s.completed && <span className="text-xs text-red-500">Required</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}
