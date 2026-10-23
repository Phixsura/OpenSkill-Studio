"use client";

interface NextStep { label: string; path: string; }
interface InstallConfirmationProps { appName: string; appIcon: string;
  version: string; permissions: string[]; webhookConfigured: boolean;
  nextSteps: NextStep[]; onStep: (path: string) => void; onDone: () => void; }

export function InstallConfirmation({ appName, appIcon, version, permissions,
  webhookConfigured, nextSteps, onStep, onDone }: InstallConfirmationProps) {
  return (
    <div className="max-w-md mx-auto text-center py-8 space-y-5">
      <div>
        <span className="text-5xl">{appIcon}</span>
        <h2 className="text-xl font-bold mt-2">{appName} Installed! 🎉</h2>
        <p className="text-xs text-gray-400">v{version}</p>
      </div>
      <div className="rounded-lg bg-green-50 dark:bg-green-900/20 p-3 text-sm text-green-700">
        ✅ {permissions.length} permissions granted
        {webhookConfigured && " · Webhook configured"}
      </div>
      <div className="text-left space-y-2">
        <p className="text-xs font-semibold text-gray-400">Next Steps</p>
        {nextSteps.map(s => (
          <button key={s.path} onClick={() => onStep(s.path)}
            className="w-full text-left text-sm bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700">
            → {s.label}
          </button>
        ))}
      </div>
      <button onClick={onDone}
        className="px-8 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">Go to Dashboard</button>
    </div>
  );
}
