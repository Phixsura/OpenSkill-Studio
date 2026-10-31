"use client";

interface Step { step_id: string; title: string; completed: boolean; required: boolean; }
interface Props { consumerId: string; steps: Step[]; progressPct: number; onboarded: boolean; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerOnboardingChecklistCard({ consumerId, steps, progressPct, onboarded, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Onboarding</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${onboarded ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400"}`}>{onboarded ? "✅ Complete" : `${progressPct}%`}</span>
      </div>
      <div className="mb-3 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
        <div className="h-1.5 rounded-full bg-blue-500 transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="space-y-1">
        {steps.map((s) => (
          <div key={s.step_id} className="flex items-center gap-2 text-[11px]">
            <span>{s.completed ? "✅" : "⬜"}</span>
            <span className={`${s.completed ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-300"}`}>{s.title}</span>
            {!s.required && <span className="text-[9px] text-gray-400">(optional)</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
