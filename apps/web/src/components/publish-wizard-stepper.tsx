"use client";

interface PublishStep { id: string; title: string; description: string; completed: boolean; }
interface PublishWizardStepperProps { steps: PublishStep[]; currentStep: string | null;
  progressPct: number; readyToSubmit: boolean;
  onStep: (id: string) => void; onPublish: () => void; }

export function PublishWizardStepper({ steps, currentStep, progressPct, readyToSubmit, onStep, onPublish }: PublishWizardStepperProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">📤 Publish to Marketplace</h3>
        <span className="text-sm font-bold">{progressPct}%</span>
      </div>
      <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full mb-4">
        <div className="h-full bg-blue-500 rounded-full" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="space-y-2 mb-4">
        {steps.map(s => (
          <button key={s.id} onClick={() => onStep(s.id)}
            className={`w-full text-left flex items-center gap-3 p-2.5 rounded-lg ${
              s.id === currentStep ? "bg-blue-50 dark:bg-blue-900/20 ring-1 ring-blue-300" :
              s.completed ? "bg-green-50 dark:bg-green-900/10" : "hover:bg-gray-50 dark:hover:bg-gray-800"
            }`}>
            <span>{s.completed ? "✅" : s.id === currentStep ? "🔵" : "⬜"}</span>
            <div>
              <p className="text-sm font-medium">{s.title}</p>
              <p className="text-xs text-gray-400">{s.description}</p>
            </div>
          </button>
        ))}
      </div>
      <button onClick={onPublish} disabled={!readyToSubmit}
        className="w-full py-2.5 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50">
        {readyToSubmit ? "🚀 Submit for Review" : `${steps.filter(s => !s.completed).length} steps remaining`}
      </button>
    </div>
  );
}
