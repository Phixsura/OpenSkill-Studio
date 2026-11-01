"use client";

interface Step { id: string; title: string; description: string; }
interface WizardProgressCardProps { steps: Step[]; completedSteps: string[]; pct: number; currentStep: Step | null; }

export function WizardProgressCard({ steps, completedSteps, pct, currentStep }: WizardProgressCardProps) {
  const completed = new Set(completedSteps);
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-semibold">🧙 App Creation Wizard</h4>
        <span className="text-sm font-medium">{pct}%</span>
      </div>
      <div className="mb-3 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-2 rounded-full bg-blue-500" style={{ width: `${pct}%` }} />
      </div>
      {currentStep && <p className="mb-3 text-sm text-blue-600">👉 Next: {currentStep.title}</p>}
      <ol className="space-y-1">
        {steps.map((s, i) => (
          <li key={s.id} className="flex items-center gap-2 text-sm">
            <span>{completed.has(s.id) ? "✅" : `${i + 1}.`}</span>
            <span className={completed.has(s.id) ? "text-gray-400 line-through" : ""}>{s.title}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}
