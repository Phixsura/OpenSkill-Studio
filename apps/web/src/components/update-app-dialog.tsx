"use client";

interface UpdateAppDialogProps {
  appName: string;
  currentVersion: string;
  targetVersion: string;
  breakingChanges: string[];
  onConfirm: () => void;
  onCancel: () => void;
}

export function UpdateAppDialog({ appName, currentVersion, targetVersion, breakingChanges, onConfirm, onCancel }: UpdateAppDialogProps) {
  const hasBreaking = breakingChanges.length > 0;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" role="dialog" aria-label="Update app">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
        <h2 className="text-lg font-semibold">Update {appName}</h2>
        <p className="mt-1 text-sm text-gray-500">{currentVersion} → {targetVersion}</p>
        {hasBreaking && (
          <div className="mt-4 rounded border border-yellow-300 bg-yellow-50 p-3 dark:border-yellow-600 dark:bg-yellow-900/20">
            <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">⚠️ Breaking Changes</p>
            <ul className="mt-1 list-inside list-disc text-sm text-yellow-700 dark:text-yellow-300">
              {breakingChanges.map((c, i) => <li key={i}>{c}</li>)}
            </ul>
          </div>
        )}
        <div className="mt-6 flex justify-end gap-3">
          <button onClick={onCancel} className="rounded px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">Cancel</button>
          <button onClick={onConfirm} className={`rounded px-4 py-2 text-sm text-white ${hasBreaking ? "bg-yellow-600 hover:bg-yellow-700" : "bg-blue-600 hover:bg-blue-700"}`}>
            {hasBreaking ? "Update Anyway" : "Update"}
          </button>
        </div>
      </div>
    </div>
  );
}
