"use client";

interface StateCount { state: string; count: number; }
interface Props { states: StateCount[]; totalConsumers: number; appName: string; }

const stateIcon: Record<string, string> = { registered: "📝", onboarding: "🚀", active: "✅", suspended: "⏸️", offboarding: "📤", deactivated: "🚫" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerLifecycleCard({ states, totalConsumers, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Consumer Lifecycle</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {totalConsumers} consumers</p>
        </div>
      </div>
      {states.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No consumers</p>
      ) : (
        <div className="space-y-1">
          {states.map((s) => (
            <div key={s.state} className="flex items-center justify-between text-[11px]">
              <span className="text-gray-700 dark:text-gray-300">{stateIcon[s.state] ?? "•"} {s.state}</span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">{s.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
