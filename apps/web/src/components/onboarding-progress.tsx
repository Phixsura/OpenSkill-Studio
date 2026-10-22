"use client";

interface Step { key: string; label: string; required: boolean; completed: boolean; }

interface OnboardingProgressProps {
  steps: Step[];
  progressPct: number;
  requiredComplete: boolean;
  nextStep: { key: string; label: string } | null;
}

export function OnboardingProgress({ steps, progressPct, requiredComplete, nextStep }: OnboardingProgressProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold">Getting Started</h3>
        <span className="text-sm font-medium">{progressPct}%</span>
      </div>
      <div className="mb-4 h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-2 rounded-full bg-blue-500 transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      {nextStep && !requiredComplete && (
        <p className="mb-3 text-sm text-blue-600 dark:text-blue-400">
          👉 Next: {nextStep.label}
        </p>
      )}
      {requiredComplete && (
        <p className="mb-3 text-sm text-green-600 dark:text-green-400">🎉 All required steps complete!</p>
      )}
      <ul className="space-y-1">
        {steps.map(s => (
          <li key={s.key} className="flex items-center gap-2 text-sm">
            <span>{s.completed ? "✅" : "⬜"}</span>
            <span className={s.completed ? "text-gray-500 line-through" : ""}>{s.label}</span>
            {s.required && !s.completed && <span className="text-xs text-red-400">required</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}
