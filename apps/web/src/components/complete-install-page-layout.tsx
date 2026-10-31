"use client";

interface Step { key: string; title: string; required: boolean; }
interface Blocker { message: string; }
interface CompleteInstallPageLayoutProps {
  appName: string; developerName: string; developerVerified: boolean;
  canInstall: boolean; blockers: Blocker[]; steps: Step[];
  ctaLabel: string; onInstall: () => void;
}

export function CompleteInstallPageLayout({ appName, developerName, developerVerified, canInstall, blockers, steps, ctaLabel, onInstall }: CompleteInstallPageLayoutProps) {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Install {appName}</h1>
        <p className="text-sm text-gray-500">by {developerName} {developerVerified && "✅"}</p>
      </div>
      {blockers.length > 0 && (
        <div className="rounded-lg bg-red-50 p-4 dark:bg-red-900/20">
          <p className="text-sm font-semibold text-red-700">Cannot Install</p>
          {blockers.map((b, i) => <p key={i} className="text-xs text-red-600">{b.message}</p>)}
        </div>
      )}
      <div className="space-y-3">
        {steps.map((s, i) => (
          <div key={s.key} className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">{i + 1}</span>
              <h3 className="font-semibold">{s.title}</h3>
              {s.required && <span className="text-xs text-red-500">Required</span>}
            </div>
          </div>
        ))}
      </div>
      <button onClick={onInstall} disabled={!canInstall}
        className="w-full rounded-lg bg-blue-600 py-3 text-sm font-semibold text-white disabled:opacity-50">
        {ctaLabel}
      </button>
    </div>
  );
}
