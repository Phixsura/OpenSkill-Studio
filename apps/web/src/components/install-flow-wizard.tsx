"use client";

interface InstallStep { id: string; label: string; icon: string; }
interface InstallFlowWizardProps { appName: string; steps: InstallStep[];
  currentStep: number; permissions: string[];
  onNext: () => void; onBack: () => void; onInstall: () => void; }

export function InstallFlowWizard({ appName, steps, currentStep, permissions,
  onNext, onBack, onInstall }: InstallFlowWizardProps) {
  const isFinal = currentStep === steps.length - 1;
  const isFirst = currentStep === 0;
  const step = steps[currentStep];
  const pct = Math.round((currentStep / (steps.length - 1)) * 100);

  return (
    <div className="mx-auto max-w-lg space-y-5">
      <h2 className="text-lg font-bold">Install {appName}</h2>
      <div className="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
        <div className="h-full rounded-full bg-blue-600 transition-all" style={{ width: `${pct}%` }} />
      </div>
      <div className="flex justify-between">
        {steps.map((s, i) => (
          <div key={s.id} className={`flex flex-col items-center gap-1 ${i <= currentStep ? "" : "opacity-40"}`}>
            <span className="text-lg">{s.icon}</span>
            <span className="text-xs">{s.label}</span>
          </div>
        ))}
      </div>
      <div className="rounded-lg border p-4 dark:border-gray-700">
        <h3 className="text-sm font-semibold">{step?.icon} {step?.label}</h3>
        {currentStep === 0 && (
          <div className="mt-3 space-y-1">
            <p className="text-xs text-gray-400 mb-2">This app requests:</p>
            {permissions.map(p => (
              <div key={p} className="flex items-center gap-2 text-sm">
                <span className="text-green-500">✓</span>{p}
              </div>
            ))}
          </div>
        )}
      </div>
      <div className="flex justify-between">
        <button onClick={onBack} disabled={isFirst}
          className="rounded border px-4 py-2 text-sm disabled:opacity-30 dark:border-gray-700">Back</button>
        {isFinal ? (
          <button onClick={onInstall} className="rounded bg-green-600 px-4 py-2 text-sm text-white font-medium">Install</button>
        ) : (
          <button onClick={onNext} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Next</button>
        )}
      </div>
    </div>
  );
}
