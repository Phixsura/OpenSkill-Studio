"use client";

interface OnboardingStep { id: string; title: string; description: string; completed: boolean; index: number; }
interface OnboardingWizardProps { steps: OnboardingStep[]; progressPct: number;
  completedCount: number; total: number; onComplete: (stepId: string) => void; }

export function OnboardingWizard({ steps, progressPct, completedCount, total, onComplete }: OnboardingWizardProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700 max-w-lg">
      <h3 className="font-semibold mb-1">🚀 Get Started</h3>
      <p className="text-xs text-gray-400 mb-3">{completedCount}/{total} complete · {progressPct}%</p>
      <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full mb-4 overflow-hidden">
        <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="space-y-2">
        {steps.map(s => (
          <div key={s.id} className={`flex items-center gap-3 rounded-lg px-3 py-2.5 transition ${
            s.completed ? "bg-green-50 dark:bg-green-900/10" : "bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700"
          }`}>
            <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs border-2 ${
              s.completed ? "bg-green-500 border-green-500 text-white" : "border-gray-300 dark:border-gray-600"
            }`}>{s.completed ? "✓" : s.index + 1}</span>
            <div className="flex-1">
              <p className={`text-sm font-medium ${s.completed ? "line-through text-gray-400" : ""}`}>{s.title}</p>
              <p className="text-xs text-gray-400">{s.description}</p>
            </div>
            {!s.completed && (
              <button onClick={() => onComplete(s.id)}
                className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Start</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
