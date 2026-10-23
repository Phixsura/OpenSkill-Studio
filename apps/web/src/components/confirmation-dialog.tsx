"use client";

import { useState } from "react";

interface ConfirmationDialogProps { title: string; icon: string; message: string;
  danger: boolean; confirmText: string | null; cancelLabel: string;
  onConfirm: () => void; onCancel: () => void; }

export function ConfirmationDialog({ title, icon, message, danger, confirmText,
  cancelLabel, onConfirm, onCancel }: ConfirmationDialogProps) {
  const [typed, setTyped] = useState("");
  const needsTyping = confirmText !== null;
  const canConfirm = !needsTyping || typed === confirmText;
  return (
    <div className="mx-auto max-w-md rounded-lg border bg-white p-6 shadow-xl dark:border-gray-700 dark:bg-gray-900">
      <div className="text-center">
        <span className="text-4xl">{icon}</span>
        <h2 className="mt-2 text-xl font-bold">{title}</h2>
        <p className="mt-2 text-sm text-gray-500">{message}</p>
      </div>
      {needsTyping && (
        <div className="mt-4">
          <p className="text-xs text-gray-400">Type <strong>{confirmText}</strong> to confirm:</p>
          <input value={typed} onChange={e => setTyped(e.target.value)}
            className="mt-1 w-full rounded border px-3 py-2 font-mono text-sm dark:border-gray-600 dark:bg-gray-700"
            placeholder={confirmText ?? ""} />
        </div>
      )}
      <div className="mt-4 flex gap-2">
        <button onClick={onCancel}
          className="flex-1 rounded border py-2 text-sm dark:border-gray-600">{cancelLabel}</button>
        <button onClick={onConfirm} disabled={!canConfirm}
          className={`flex-1 rounded py-2 text-sm font-semibold text-white disabled:opacity-50 ${danger ? "bg-red-600" : "bg-blue-600"}`}>
          Confirm
        </button>
      </div>
    </div>
  );
}
