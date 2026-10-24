"use client";

interface WizardStep { index: number; title: string; status: string; }
interface IntegrationWizardStepsProps { name: string; icon: string;
  steps: WizardStep[]; progressPct: number; currentStep: number;
  onNext: () => void; onBack: () => void; }

export function IntegrationWizardSteps({ name, icon, steps, progressPct, currentStep, onNext, onBack }: IntegrationWizardStepsProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700 max-w-md">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-2xl">{icon}</span>
        <h3 className="font-bold">Connect {name}</h3>
      </div>
      <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full mb-4">
        <div className="h-full bg-blue-500 rounded-full" style={{ width: `${progressPct}%` }} />
      </div>
      <div className="space-y-2 mb-4">
        {steps.map(s => (
          <div key={s.index} className={`flex items-center gap-2 text-sm ${
            s.status === "current" ? "font-medium" : s.status === "completed" ? "text-gray-400" : "text-gray-300"
          }`}>
            <span>{s.status === "completed" ? "✅" : s.status === "current" ? "🔵" : "⬜"}</span>
            {s.title}
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        {currentStep > 0 && (
          <button onClick={onBack} className="flex-1 py-2 border rounded text-sm">Back</button>
        )}
        <button onClick={onNext}
          className="flex-1 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
          {currentStep === steps.length - 1 ? "Complete" : "Next"}
        </button>
      </div>
    </div>
  );
}
