"use client";

interface Step { id: string; title: string; icon: string; time_min: number; completed: boolean; }
interface GettingStartedPageProps { developerName: string; steps: Step[]; completed: number;
  total: number; pct: number; currentStep: Step | null; remainingTimeMin: number;
  allDone: boolean; onStepClick: (id: string) => void; }

export function GettingStartedPage({ developerName, steps, completed, total, pct,
  currentStep, remainingTimeMin, allDone, onStepClick }: GettingStartedPageProps) {
  return (
    <div className="mx-auto max-w-lg space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold">Welcome, {developerName}! 👋</h1>
        <p className="mt-1 text-sm text-gray-400">
          {allDone ? "🎉 All set! Start building!" : `${remainingTimeMin} min remaining`}
        </p>
      </div>
      <div>
        <div className="flex justify-between text-sm">
          <span>{completed}/{total} completed</span>
          <span className="font-bold">{pct}%</span>
        </div>
        <div className="mt-1 h-3 rounded-full bg-gray-200 dark:bg-gray-700">
          <div className={`h-full rounded-full transition-all ${allDone ? "bg-green-500" : "bg-blue-600"}`}
            style={{ width: `${pct}%` }} />
        </div>
      </div>
      <div className="space-y-2">
        {steps.map((s, i) => (
          <button key={s.id} onClick={() => onStepClick(s.id)}
            className={`flex w-full items-center gap-3 rounded-lg border p-3 text-left ${s.id === currentStep?.id ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : s.completed ? "opacity-60" : ""} dark:border-gray-700`}>
            <span className={`flex h-8 w-8 items-center justify-center rounded-full text-sm ${s.completed ? "bg-green-500 text-white" : s.id === currentStep?.id ? "bg-blue-600 text-white" : "border-2 dark:border-gray-600"}`}>
              {s.completed ? "✓" : s.icon}
            </span>
            <div className="flex-1">
              <p className={`text-sm font-medium ${s.completed ? "line-through text-gray-400" : ""}`}>{s.title}</p>
              <p className="text-xs text-gray-400">~{s.time_min} min</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
