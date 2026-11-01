"use client";

interface Step { index: number; title: string; description: string; icon: string; status: string; optional: boolean; }
interface StepWizardProps { steps: Step[]; progressPct: number; onBack: () => void; onNext: () => void;
  canGoBack: boolean; canGoNext: boolean; isFinal: boolean; }

const statusStyles: Record<string, string> = {
  completed: "bg-green-500 text-white",
  current: "bg-blue-600 text-white ring-2 ring-blue-300",
  upcoming: "bg-gray-200 text-gray-500 dark:bg-gray-700 dark:text-gray-400",
};

export function StepWizard({ steps, progressPct, onBack, onNext, canGoBack, canGoNext, isFinal }: StepWizardProps) {
  return (
    <div className="space-y-6">
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="flex justify-between">
        {steps.map(s => (
          <div key={s.index} className="flex flex-col items-center gap-1.5">
            <div className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium ${statusStyles[s.status]}`}>
              {s.status === "completed" ? "✓" : s.icon}
            </div>
            <span className="text-xs font-medium">{s.title}</span>
          </div>
        ))}
      </div>
      <div className="flex justify-between">
        <button onClick={onBack} disabled={!canGoBack}
          className="rounded px-4 py-2 text-sm border disabled:opacity-30 dark:border-gray-700">Back</button>
        <button onClick={onNext} disabled={!canGoNext && !isFinal}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-30">
          {isFinal ? "Finish" : "Next"}
        </button>
      </div>
    </div>
  );
}
