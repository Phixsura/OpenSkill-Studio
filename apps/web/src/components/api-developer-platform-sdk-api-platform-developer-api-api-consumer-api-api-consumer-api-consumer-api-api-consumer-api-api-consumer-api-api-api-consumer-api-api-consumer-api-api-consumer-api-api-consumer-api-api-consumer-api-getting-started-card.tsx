"use client";

interface Step { id: string; title: string; description: string; completed: boolean; codeSnippet: string; }
interface Props { steps: Step[]; progressPct: number; done: boolean; nextStepId: string | null; consumerId: string; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiApiConsumerApiGettingStartedCard({ steps, progressPct, done, nextStepId, consumerId, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🚀 Getting Started</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
        </div>
        <span className={`text-sm font-bold ${done ? "text-green-600" : "text-blue-600"}`}>{progressPct}%</span>
      </div>
      <div className="mb-3 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className={`h-full rounded-full transition-all ${done ? "bg-green-500" : "bg-blue-500"}`} style={{ width: `${progressPct}%` }} />
      </div>
      {done && <div className="mb-3 rounded bg-green-50 p-2 text-center text-[11px] text-green-700 dark:bg-green-900/20 dark:text-green-400">🎉 All set! You are ready to go.</div>}
      <div className="space-y-1">
        {steps.map((s) => (
          <div key={s.id} className={`flex items-start gap-2 rounded p-1.5 text-[11px] ${s.id === nextStepId ? "bg-blue-50 dark:bg-blue-900/10" : ""}`}>
            <span className="mt-0.5">{s.completed ? "✅" : s.id === nextStepId ? "👉" : "⬜"}</span>
            <div>
              <span className={s.completed ? "text-gray-400 line-through" : "font-medium text-gray-700 dark:text-gray-300"}>{s.title}</span>
              {s.id === nextStepId && <div className="text-[10px] text-gray-400">{s.description}</div>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
