"use client";

interface WizardStep { id: string; title: string; description: string; required: boolean; completed: boolean; }
interface OnboardingWizardFlowProps { steps: WizardStep[]; currentStep: string | null;
  progressPct: number; canSubmit: boolean; onStepClick: (id: string) => void; onSubmit: () => void; }

export function OnboardingWizardFlow({ steps, currentStep, progressPct, canSubmit, onStepClick, onSubmit }: OnboardingWizardFlowProps) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">Create Your App</h2>
        <div className="mt-2 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${progressPct}%` }} />
        </div>
        <p className="mt-1 text-xs text-gray-400">{progressPct}% complete</p>
      </div>
      <div className="space-y-1.5">
        {steps.map((s, i) => (
          <button key={s.id} onClick={() => onStepClick(s.id)}
            className={`flex w-full items-center gap-3 rounded-lg border p-3 text-left ${s.id === currentStep ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "dark:border-gray-700"}`}>
            <span className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold ${s.completed ? "bg-green-500 text-white" : s.id === currentStep ? "bg-blue-600 text-white" : "border dark:border-gray-600"}`}>
              {s.completed ? "✓" : i + 1}
            </span>
            <div className="flex-1">
              <p className={`text-sm ${s.completed ? "text-gray-400 line-through" : "font-medium"}`}>{s.title}</p>
              <p className="text-xs text-gray-400">{s.description}</p>
            </div>
            {s.required && !s.completed && <span className="text-[10px] text-red-400">Required</span>}
          </button>
        ))}
      </div>
      <button onClick={onSubmit} disabled={!canSubmit}
        className="w-full rounded-lg bg-green-600 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
        {canSubmit ? "🚀 Submit for Review" : "Complete required steps"}
      </button>
    </div>
  );
}
