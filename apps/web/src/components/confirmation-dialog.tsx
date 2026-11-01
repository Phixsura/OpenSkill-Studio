"use client";

import { useState } from "react";

interface ConfirmationDialogProps { title: string; message: string; icon: string;
  severity: string; confirmText: string; requiresTextInput: boolean;
  onConfirm: () => void; onCancel: () => void; }

export function ConfirmationDialog({ title, message, icon, severity, confirmText,
  requiresTextInput, onConfirm, onCancel }: ConfirmationDialogProps) {
  const [input, setInput] = useState("");
  const canConfirm = !requiresTextInput || input === confirmText;
  const btnColor = severity === "danger" ? "bg-red-600" : "bg-yellow-600";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onCancel}>
      <div className="w-full max-w-sm rounded-xl border bg-white p-5 shadow-xl dark:bg-gray-900 dark:border-gray-700" onClick={e => e.stopPropagation()}>
        <div className="flex items-center gap-3 mb-3">
          <span className="text-2xl">{icon}</span>
          <h3 className="text-lg font-bold">{title}</h3>
        </div>
        <p className="text-sm text-gray-500">{message}</p>
        {requiresTextInput && (
          <div className="mt-3">
            <p className="text-xs text-gray-400 mb-1">Type <strong>{confirmText}</strong> to confirm</p>
            <input value={input} onChange={e => setInput(e.target.value)}
              className="w-full rounded border px-3 py-2 text-sm font-mono dark:bg-gray-800 dark:border-gray-600" />
          </div>
        )}
        <div className="mt-4 flex justify-end gap-2">
          <button onClick={onCancel} className="rounded border px-4 py-2 text-sm dark:border-gray-700">Cancel</button>
          <button onClick={onConfirm} disabled={!canConfirm}
            className={`rounded px-4 py-2 text-sm text-white disabled:opacity-30 ${btnColor}`}>{confirmText}</button>
        </div>
      </div>
    </div>
  );
}
