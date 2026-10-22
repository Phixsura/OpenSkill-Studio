"use client";

interface GuideStep { step: number; title: string; description: string; docsUrl: string; }

interface GettingStartedGuideProps { steps: GuideStep[]; completedSteps: number[]; }

export function GettingStartedGuide({ steps, completedSteps }: GettingStartedGuideProps) {
  const completed = new Set(completedSteps);
  const pct = steps.length > 0 ? Math.round((completedSteps.length / steps.length) * 100) : 0;

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold">🚀 Getting Started</h3>
        <span className="text-sm">{pct}% complete</span>
      </div>
      <div className="mb-4 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-2 rounded-full bg-blue-500 transition-all" style={{ width: `${pct}%` }} />
      </div>
      <ol className="space-y-3">
        {steps.map(s => (
          <li key={s.step} className={`flex gap-3 ${completed.has(s.step) ? "opacity-60" : ""}`}>
            <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs ${
              completed.has(s.step) ? "bg-green-500 text-white" : "bg-gray-200 dark:bg-gray-700"
            }`}>{completed.has(s.step) ? "✓" : s.step}</span>
            <div>
              <p className={`text-sm font-medium ${completed.has(s.step) ? "line-through" : ""}`}>{s.title}</p>
              <p className="text-xs text-gray-500">{s.description}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
