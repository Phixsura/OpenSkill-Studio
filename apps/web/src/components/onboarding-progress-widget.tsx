"use client";

interface OnboardingStep { id: string; title: string; completed: boolean; }
interface OnboardingProgressWidgetProps { steps: OnboardingStep[]; progressPct: number;
  completedCount: number; totalSteps: number; message: string | null;
  onStart: (stepId: string) => void; }

export function OnboardingProgressWidget({ steps, progressPct, completedCount,
  totalSteps, message, onStart }: OnboardingProgressWidgetProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🚀 Getting Started</h3>
        <span className="text-sm font-bold">{progressPct}%</span>
      </div>
      <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full mb-4 overflow-hidden">
        <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      {message && <p className="text-sm text-center mb-3">{message}</p>}
      <div className="space-y-1.5">
        {steps.map(s => (
          <div key={s.id} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <span>{s.completed ? "✅" : "⬜"}</span>
              <span className={s.completed ? "line-through text-gray-400" : ""}>{s.title}</span>
            </div>
            {!s.completed && (
              <button onClick={() => onStart(s.id)}
                className="text-xs px-2 py-0.5 bg-blue-600 text-white rounded hover:bg-blue-700">Start</button>
            )}
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-400 text-center mt-3">{completedCount}/{totalSteps} complete</p>
    </div>
  );
}
