"use client";
import { useState } from "react";

interface ConfirmDialogProps { title: string; body: string; confirmLabel: string;
  variant: string; requiresName: boolean; resourceName: string;
  onConfirm: () => void; onCancel: () => void; }

const VARIANT_STYLE: Record<string, string> = {
  danger: "bg-red-600 hover:bg-red-700", warning: "bg-yellow-600 hover:bg-yellow-700",
  primary: "bg-blue-600 hover:bg-blue-700",
};

export function ConfirmDialog({ title, body, confirmLabel, variant, requiresName,
  resourceName, onConfirm, onCancel }: ConfirmDialogProps) {
  const [input, setInput] = useState("");
  const canConfirm = !requiresName || input === resourceName;
  return (
    <div className="rounded-xl border dark:border-gray-700 p-5 max-w-md shadow-xl bg-white dark:bg-gray-900">
      <h3 className="text-lg font-bold mb-2">{title}</h3>
      <p className="text-sm text-gray-500 mb-4">{body}</p>
      {requiresName && (
        <input value={input} onChange={e => setInput(e.target.value)} placeholder={resourceName}
          className="w-full text-sm px-3 py-1.5 border rounded mb-4 dark:bg-gray-800 dark:border-gray-600" />
      )}
      <div className="flex gap-2 justify-end">
        <button onClick={onCancel}
          className="px-4 py-2 text-sm border rounded hover:bg-gray-50 dark:hover:bg-gray-800">Cancel</button>
        <button onClick={onConfirm} disabled={!canConfirm}
          className={`px-4 py-2 text-sm text-white rounded disabled:opacity-50 ${VARIANT_STYLE[variant] || VARIANT_STYLE.primary}`}>
          {confirmLabel}
        </button>
      </div>
    </div>
  );
}
