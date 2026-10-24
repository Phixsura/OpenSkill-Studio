"use client";

interface Blocker { type: string; message: string; }
interface Warning { type: string; message: string; }
interface InstallGuardDialogProps { canInstall: boolean; blockers: Blocker[]; warnings: Warning[]; onProceed: () => void; onCancel: () => void; }

export function InstallGuardDialog({ canInstall, blockers, warnings, onProceed, onCancel }: InstallGuardDialogProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      {blockers.length > 0 && (
        <div className="mb-3 rounded bg-red-50 p-3 dark:bg-red-900/20">
          <p className="text-sm font-semibold text-red-700 dark:text-red-300">❌ Cannot Install</p>
          <ul className="mt-1 space-y-1">
            {blockers.map((b, i) => <li key={i} className="text-xs text-red-600">{b.message}</li>)}
          </ul>
        </div>
      )}
      {warnings.length > 0 && (
        <div className="mb-3 rounded bg-yellow-50 p-3 dark:bg-yellow-900/20">
          <p className="text-sm font-semibold text-yellow-700 dark:text-yellow-300">⚠️ Warnings</p>
          <ul className="mt-1 space-y-1">
            {warnings.map((w, i) => <li key={i} className="text-xs text-yellow-600">{w.message}</li>)}
          </ul>
        </div>
      )}
      <div className="flex justify-end gap-2">
        <button onClick={onCancel} className="rounded px-4 py-2 text-sm text-gray-600">Cancel</button>
        <button onClick={onProceed} disabled={!canInstall}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50">
          {canInstall ? "Install" : "Cannot Install"}
        </button>
      </div>
    </div>
  );
}
