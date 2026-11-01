"use client";

interface StepInfo { step_id: string; title: string; completed: boolean; skippable: boolean; order: number; }
interface Props { consumerId: string; steps: StepInfo[]; progressPct: number; isComplete: boolean; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiOnboardingWizardCard({ consumerId, steps, progressPct, isComplete, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🧙 Onboarding Wizard</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={`text-sm font-bold ${isComplete ? "text-green-600 dark:text-green-400" : "text-gray-400"}`}>{isComplete ? "✅ Done" : `${progressPct}%`}</span>
      </div>
      <div className="mb-3 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
        <div className="h-1.5 rounded-full bg-blue-500" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="space-y-1">
        {steps.map((s) => (
          <div key={s.step_id} className="flex items-center gap-2 text-[11px]">
            <span>{s.completed ? "✅" : "⬜"}</span>
            <span className={s.completed ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-300"}>{s.title}</span>
            {s.skippable && !s.completed && <span className="text-[9px] text-gray-400">(optional)</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
