"use client";

interface InstallStep { id: string; label: string; status: string; }
interface AppInstallWizardProps { appName: string; steps: InstallStep[];
  permissions: string[]; onAcceptPermissions: () => void; onComplete: (stepId: string) => void; }

const stepIcon = (s: string) => s === "completed" ? "✅" : s === "current" ? "🔵" : "⬜";

export function AppInstallWizard({ appName, steps, permissions, onAcceptPermissions, onComplete }: AppInstallWizardProps) {
  const currentStep = steps.find(s => s.status === "current");
  return (
    <div className="mx-auto max-w-md space-y-4">
      <h2 className="text-center text-lg font-semibold">Install {appName}</h2>
      <div className="flex justify-center gap-2">
        {steps.map((s, i) => (
          <div key={s.id} className="flex items-center gap-1">
            <span>{stepIcon(s.status)}</span>
            {i < steps.length - 1 && <div className="h-px w-6 bg-gray-300 dark:bg-gray-600" />}
          </div>
        ))}
      </div>
      {currentStep?.id === "review_permissions" && (
        <div className="space-y-3 rounded-lg border p-4 dark:border-gray-700">
          <h3 className="font-medium">Permissions Requested</h3>
          <ul className="space-y-1">
            {permissions.map(p => (
              <li key={p} className="flex items-center gap-2 text-sm">
                <span className="text-green-500">✓</span> {p}
              </li>
            ))}
          </ul>
          <button onClick={onAcceptPermissions}
            className="w-full rounded bg-blue-600 py-2 text-sm font-medium text-white">
            Accept & Continue
          </button>
        </div>
      )}
      {currentStep && currentStep.id !== "review_permissions" && (
        <div className="text-center">
          <p className="text-sm text-gray-400">{currentStep.label}</p>
          <button onClick={() => onComplete(currentStep.id)}
            className="mt-2 rounded bg-blue-600 px-4 py-2 text-sm text-white">Continue</button>
        </div>
      )}
    </div>
  );
}
