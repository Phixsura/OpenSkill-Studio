"use client";

interface RollbackDialogProps {
  appName: string; fromVersion: string; toVersion: string;
  onConfirm: () => void; onCancel: () => void;
}

export function RollbackDialog({ appName, fromVersion, toVersion, onConfirm, onCancel }: RollbackDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" role="dialog" aria-label="Rollback">
      <div className="w-full max-w-sm rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
        <div className="text-center text-3xl">⏪</div>
        <h2 className="mt-2 text-center text-lg font-semibold">Rollback {appName}</h2>
        <p className="mt-2 text-center text-sm text-gray-500">
          {fromVersion} → {toVersion}
        </p>
        <div className="mt-4 rounded bg-yellow-50 p-3 text-xs text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300">
          ⚠️ Configuration may need manual adjustment after rollback.
        </div>
        <div className="mt-4 flex justify-center gap-3">
          <button onClick={onCancel} className="rounded px-4 py-2 text-sm text-gray-600">Cancel</button>
          <button onClick={onConfirm} className="rounded bg-orange-600 px-4 py-2 text-sm text-white hover:bg-orange-700">Rollback</button>
        </div>
      </div>
    </div>
  );
}
