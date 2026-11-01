"use client";

interface Step { id: string; title: string; breaking: boolean; completed: boolean; }
interface Props { fromVersion: string; toVersion: string; title: string; steps: Step[]; progressPct: number; complete: boolean; breakingRemaining: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiMigrationGuideCard({ fromVersion, toVersion, title, steps, progressPct, complete, breakingRemaining, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Migration Guide</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {fromVersion} → {toVersion}</p>
        </div>
        <span className={`text-sm font-bold ${complete ? "text-green-600" : "text-blue-600"}`}>{progressPct}%</span>
      </div>
      <div className="mb-3 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full ${complete ? "bg-green-500" : "bg-blue-500"}`} style={{ width: `${progressPct}%` }} />
      </div>
      {breakingRemaining > 0 && <div className="mb-2 text-[10px] text-red-500">⚠️ {breakingRemaining} breaking changes remaining</div>}
      <div className="space-y-1">
        {steps.map((s) => (
          <div key={s.id} className="flex items-center gap-2 text-[11px]">
            <span>{s.completed ? "✅" : "⬜"}</span>
            <span className={s.completed ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-300"}>{s.title}</span>
            {s.breaking && !s.completed && <span className="text-[9px] text-red-400">breaking</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
