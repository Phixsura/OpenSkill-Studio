"use client";

interface PhaseInfo { phase_id: string; name: string; completed: boolean; required: boolean; }
interface Props { consumerId: string; phases: PhaseInfo[]; completionPct: number; currentPhase: string; ready: boolean; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerOnboardingProgressCard({ consumerId, phases, completionPct, currentPhase, ready, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚀 Onboarding Progress</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={`text-sm font-bold ${ready ? "text-green-600 dark:text-green-400" : "text-gray-400"}`}>{ready ? "✅ Ready" : `${completionPct}%`}</span>
      </div>
      <div className="mb-2 h-1.5 w-full rounded-full bg-gray-100 dark:bg-gray-800">
        <div className="h-1.5 rounded-full bg-blue-500" style={{ width: `${completionPct}%` }} />
      </div>
      <div className="space-y-1">
        {phases.map((p) => (
          <div key={p.phase_id} className="flex items-center gap-2 text-[11px]">
            <span>{p.completed ? "✅" : "⬜"}</span>
            <span className={p.completed ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-300"}>{p.name}</span>
            {!p.required && <span className="text-[9px] text-gray-400">(optional)</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
