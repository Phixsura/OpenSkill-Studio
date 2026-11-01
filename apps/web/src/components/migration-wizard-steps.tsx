"use client";

interface Step { step: number; type: string; description: string; automated: boolean; risk: string; }
interface MigrationWizardStepsProps { fromVersion: string; toVersion: string; steps: Step[]; onRunAuto: () => void; }

const riskColors: Record<string, string> = {
  low: "text-green-600", medium: "text-yellow-600", high: "text-red-600",
};

export function MigrationWizardSteps({ fromVersion, toVersion, steps, onRunAuto }: MigrationWizardStepsProps) {
  const hasAuto = steps.some(s => s.automated);
  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-lg font-semibold">Migration Guide</h2>
        <p className="text-sm text-gray-400">v{fromVersion} → v{toVersion}</p>
      </div>
      <div className="space-y-2">
        {steps.map(s => (
          <div key={s.step} className="flex items-start gap-3 rounded-lg border p-3 dark:border-gray-700">
            <div className={`flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full text-xs font-bold ${s.automated ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30" : "bg-gray-100 text-gray-600 dark:bg-gray-800"}`}>
              {s.step}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium">{s.description}</p>
                {s.automated && <span className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700 dark:bg-blue-900/30">Auto</span>}
              </div>
              <p className={`mt-0.5 text-xs ${riskColors[s.risk] ?? ""}`}>Risk: {s.risk}</p>
            </div>
          </div>
        ))}
      </div>
      {hasAuto && (
        <button onClick={onRunAuto} className="w-full rounded-lg bg-blue-600 py-2 text-sm font-medium text-white">
          Run Automated Steps
        </button>
      )}
    </div>
  );
}
