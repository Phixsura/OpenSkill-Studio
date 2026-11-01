"use client";

interface QuickSetupWizardProps { appName: string; language: string;
  install: string; code: string; apiKey: string;
  nextSteps: string[]; estimatedTime: string; }

export function QuickSetupWizard({ appName, language, install, code, apiKey, nextSteps, estimatedTime }: QuickSetupWizardProps) {
  return (
    <div className="max-w-lg mx-auto space-y-4">
      <div className="text-center">
        <h2 className="text-xl font-bold">🚀 Quick Setup: {appName}</h2>
        <p className="text-xs text-gray-400">~{estimatedTime} · {language}</p>
      </div>
      <div className="rounded-lg bg-gray-900 p-4">
        <p className="text-xs text-gray-400 mb-1">1. Install SDK</p>
        <code className="text-sm text-green-400">{install}</code>
      </div>
      <div className="rounded-lg bg-gray-900 p-4">
        <p className="text-xs text-gray-400 mb-1">2. Initialize Client</p>
        <pre className="text-sm text-gray-300 whitespace-pre-wrap">{code}</pre>
      </div>
      <div className="rounded-xl border dark:border-gray-700 p-4">
        <p className="text-xs font-semibold text-gray-400 mb-2">Next Steps</p>
        {nextSteps.map((s, i) => (
          <div key={i} className="flex items-center gap-2 text-sm py-1">
            <span className="w-5 h-5 rounded-full bg-gray-200 dark:bg-gray-700 text-xs flex items-center justify-center">{i + 1}</span>
            {s}
          </div>
        ))}
      </div>
    </div>
  );
}
