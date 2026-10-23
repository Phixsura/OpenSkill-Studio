"use client";

interface OnboardingStep { id: string; title: string; description: string; icon: string;
  required: boolean; completed: boolean; }
interface OnboardingWizardProps { steps: OnboardingStep[]; progressPct: number;
  canSkip: boolean; nextStep: OnboardingStep | null;
  onComplete: (id: string) => void; onSkip: () => void; }

export function OnboardingWizard({ steps, progressPct, canSkip, nextStep, onComplete, onSkip }: OnboardingWizardProps) {
  return (
    <div className="mx-auto max-w-lg space-y-5">
      <div>
        <h2 className="text-xl font-bold">Welcome to OpenSkill! 🎉</h2>
        <p className="text-sm text-gray-500 mt-1">Complete these steps to get started</p>
        <div className="mt-3 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className="h-full rounded-full bg-green-500 transition-all" style={{ width: `${progressPct}%` }} />
        </div>
        <p className="mt-1 text-xs text-gray-400">{progressPct}% complete</p>
      </div>
      <div className="space-y-2">
        {steps.map(s => (
          <div key={s.id} className={`flex items-center gap-3 rounded-lg border p-3 ${s.completed ? "opacity-60" : ""} dark:border-gray-700`}>
            <span className={`flex h-8 w-8 items-center justify-center rounded-full text-sm ${s.completed ? "bg-green-500 text-white" : "bg-gray-200 dark:bg-gray-700"}`}>
              {s.completed ? "✓" : s.icon}
            </span>
            <div className="flex-1">
              <p className={`text-sm font-medium ${s.completed ? "line-through text-gray-400" : ""}`}>{s.title}</p>
              <p className="text-xs text-gray-400">{s.description}</p>
            </div>
            {!s.completed && <button onClick={() => onComplete(s.id)} className="rounded bg-blue-600 px-3 py-1 text-xs text-white">Start</button>}
          </div>
        ))}
      </div>
      {canSkip && <button onClick={onSkip} className="w-full text-center text-sm text-blue-600 hover:underline">Skip to Dashboard →</button>}
    </div>
  );
}
