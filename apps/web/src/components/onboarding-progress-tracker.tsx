"use client";

interface Step { id: string; title: string; points: number; completed: boolean; }
interface OnboardingProgressTrackerProps { steps: Step[]; progressPct: number; pointsEarned: number; pointsTotal: number; nextStep: Step | null; }

export function OnboardingProgressTracker({ steps, progressPct, pointsEarned, pointsTotal, nextStep }: OnboardingProgressTrackerProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Getting Started</h3>
        <span className="text-sm font-bold text-blue-600">{pointsEarned}/{pointsTotal} pts</span>
      </div>
      <div className="mt-2 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      <p className="mt-1 text-xs text-gray-400">{progressPct}% complete</p>
      {nextStep && (
        <div className="mt-3 rounded bg-blue-50 px-3 py-2 text-sm dark:bg-blue-900/20">
          <span className="font-medium">Next: </span>{nextStep.title} <span className="text-xs text-blue-600">(+{nextStep.points} pts)</span>
        </div>
      )}
      <ul className="mt-3 space-y-1">
        {steps.map(s => (
          <li key={s.id} className="flex items-center gap-2 text-sm">
            <span>{s.completed ? "✅" : "⬜"}</span>
            <span className={s.completed ? "line-through opacity-50" : ""}>{s.title}</span>
            <span className="ml-auto text-xs text-gray-400">{s.points} pts</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
