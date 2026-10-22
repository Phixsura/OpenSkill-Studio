"use client";

interface OnboardingChecklistProps { steps: string[]; completed: string[]; }

export function OnboardingChecklist({ steps, completed }: OnboardingChecklistProps) {
  const completedSet = new Set(completed);
  const pct = steps.length > 0 ? Math.round((completed.length / steps.length) * 100) : 0;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-semibold">Setup Checklist</h4>
        <span className="text-sm font-medium">{pct}%</span>
      </div>
      <div className="mb-3 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-2 rounded-full bg-blue-500" style={{ width: `${pct}%` }} />
      </div>
      <ul className="space-y-1">
        {steps.map(s => (
          <li key={s} className="flex items-center gap-2 text-sm">
            <span>{completedSet.has(s) ? "✅" : "⬜"}</span>
            <span className={completedSet.has(s) ? "text-gray-400 line-through" : ""}>{s}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
