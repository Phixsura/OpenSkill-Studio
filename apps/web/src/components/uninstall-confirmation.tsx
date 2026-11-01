"use client";

interface UninstallConfirmationProps {
  appName: string;
  onConfirm: () => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function UninstallConfirmation({ appName, onConfirm, onCancel, isLoading }: UninstallConfirmationProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" role="dialog" aria-label="Uninstall app">
      <div className="w-full max-w-sm rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
        <div className="mb-4 text-center text-4xl">⚠️</div>
        <h2 className="text-center text-lg font-semibold">Uninstall {appName}?</h2>
        <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          This will revoke all tokens, remove secrets, and disable event subscriptions.
          This action cannot be undone.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <button onClick={onCancel} className="rounded px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">Cancel</button>
          <button onClick={onConfirm} disabled={isLoading}
            className="rounded bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700 disabled:opacity-50">
            {isLoading ? "Uninstalling..." : "Uninstall"}
          </button>
        </div>
      </div>
    </div>
  );
}
