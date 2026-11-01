"use client";

interface OnboardStep { index: number; title: string; description: string;
  required: boolean; completed: boolean; }
interface OnboardingStepperProps { steps: OnboardStep[]; progressPct: number;
  onComplete: (index: number) => void; onSkip: (index: number) => void; }

export function OnboardingStepper({ steps, progressPct, onComplete, onSkip }: OnboardingStepperProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold">🚀 Getting Started</h3>
          <span className="text-xs text-gray-400">{progressPct}% complete</span>
        </div>
        <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
          <div className={`h-full rounded-full ${progressPct === 100 ? "bg-green-500" : "bg-blue-500"}`}
            style={{ width: `${progressPct}%` }} />
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {steps.map(s => (
          <div key={s.index} className={`flex items-center justify-between px-4 py-3 ${s.completed ? "opacity-60" : ""}`}>
            <div className="flex items-center gap-3">
              <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${s.completed ? "bg-green-500 text-white" : "bg-gray-200 dark:bg-gray-700"}`}>
                {s.completed ? "✓" : s.index + 1}
              </span>
              <div>
                <div className="text-sm font-medium">{s.title}</div>
                {s.description && <div className="text-[10px] text-gray-400">{s.description}</div>}
              </div>
            </div>
            {!s.completed && (
              <div className="flex gap-1">
                <button onClick={() => onComplete(s.index)} className="px-2 py-1 text-xs bg-blue-500 text-white rounded">Done</button>
                {!s.required && <button onClick={() => onSkip(s.index)} className="px-2 py-1 text-xs text-gray-400 hover:underline">Skip</button>}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
