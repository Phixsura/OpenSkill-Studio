"use client";

interface Item { id: string; title: string; completed: boolean; required: boolean; }
interface Props { items: Item[]; progressPct: number; fullyOnboarded: boolean; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiOnboardingChecklistCard({ items, progressPct, fullyOnboarded, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚀 Onboarding</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={`text-sm font-bold ${fullyOnboarded ? "text-green-600" : "text-blue-600"}`}>{progressPct}%</span>
      </div>
      <div className="mb-3 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full ${fullyOnboarded ? "bg-green-500" : "bg-blue-500"}`} style={{ width: `${progressPct}%` }} />
      </div>
      {items.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No checklist items</p>
      ) : (
        <div className="space-y-1">
          {items.map((i) => (
            <div key={i.id} className="flex items-center gap-2 text-[11px]">
              <span className={i.completed ? "text-green-500" : "text-gray-300"}>{i.completed ? "✅" : "⬜"}</span>
              <span className={`${i.completed ? "text-gray-400 line-through" : "text-gray-700 dark:text-gray-300"}`}>{i.title}</span>
              {!i.required && <span className="text-[9px] text-gray-400">optional</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
