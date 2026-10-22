"use client";

interface UninstallDialogProps { appName: string; warnings: string[]; destructive: boolean; onConfirm: () => void; onCancel: () => void; }

export function UninstallDialog({ appName, warnings, destructive, onConfirm, onCancel }: UninstallDialogProps) {
  return (
    <div className="rounded-lg border border-red-200 p-5 dark:border-red-800">
      <h3 className="text-lg font-semibold">Uninstall {appName}?</h3>
      {warnings.length > 0 && (
        <ul className="my-3 space-y-1">{warnings.map((w, i) => <li key={i} className="text-sm text-red-600">⚠️ {w}</li>)}</ul>
      )}
      <p className="mb-4 text-sm text-gray-500">This action cannot be undone.</p>
      <div className="flex gap-3">
        <button onClick={onCancel} className="rounded border px-4 py-2 text-sm">Cancel</button>
        <button onClick={onConfirm} className="rounded bg-red-600 px-4 py-2 text-sm text-white">Uninstall</button>
      </div>
    </div>
  );
}
