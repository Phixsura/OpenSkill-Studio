"use client";

import { useState } from "react";

interface InstallDialogProps {
  appName: string;
  requiredScopes: string[];
  onConfirm: () => void;
  onCancel: () => void;
}

export function InstallDialog({ appName, requiredScopes, onConfirm, onCancel }: InstallDialogProps) {
  const [accepted, setAccepted] = useState(false);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" role="dialog" aria-label="Install app">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
        <h2 className="text-lg font-semibold">Install {appName}</h2>
        {requiredScopes.length > 0 && (
          <div className="mt-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">This app requires the following permissions:</p>
            <ul className="mt-2 space-y-1">
              {requiredScopes.map(s => (
                <li key={s} className="flex items-center gap-2 text-sm">
                  <span className="text-yellow-500">⚠️</span> {s}
                </li>
              ))}
            </ul>
          </div>
        )}
        <label className="mt-4 flex items-center gap-2 text-sm">
          <input type="checkbox" checked={accepted} onChange={e => setAccepted(e.target.checked)} />
          I agree to grant these permissions
        </label>
        <div className="mt-6 flex justify-end gap-3">
          <button onClick={onCancel} className="rounded px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">Cancel</button>
          <button onClick={onConfirm} disabled={!accepted}
            className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50">
            Install
          </button>
        </div>
      </div>
    </div>
  );
}
