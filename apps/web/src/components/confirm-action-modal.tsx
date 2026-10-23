"use client";

import { useState, useEffect } from "react";

interface ConfirmActionModalProps { action: string; resourceName: string; message: string;
  dangerLevel: string; requireTyping: boolean; confirmWord: string | null;
  countdownSec: number; onConfirm: () => void; onCancel: () => void; }

export function ConfirmActionModal({ action, resourceName, message, dangerLevel,
  requireTyping, confirmWord, countdownSec, onConfirm, onCancel }: ConfirmActionModalProps) {
  const [typed, setTyped] = useState("");
  const [countdown, setCountdown] = useState(countdownSec);

  useEffect(() => {
    if (countdown <= 0) return;
    const t = setInterval(() => setCountdown(c => Math.max(c - 1, 0)), 1000);
    return () => clearInterval(t);
  }, [countdown]);

  const canConfirm = countdown === 0 && (!requireTyping || typed === confirmWord);
  const bgColor = dangerLevel === "high" ? "bg-red-600" : dangerLevel === "medium" ? "bg-orange-600" : "bg-blue-600";

  return (
    <div className="mx-auto max-w-md rounded-lg border bg-white p-6 shadow-xl dark:border-gray-700 dark:bg-gray-900">
      <h2 className="text-lg font-bold capitalize">{action} {resourceName}?</h2>
      <p className="mt-2 text-sm text-gray-500">{message}</p>
      {requireTyping && confirmWord && (
        <div className="mt-3">
          <p className="text-xs text-gray-400">Type <strong className="text-red-600">{confirmWord}</strong> to confirm:</p>
          <input value={typed} onChange={e => setTyped(e.target.value)}
            className="mt-1 w-full rounded border px-3 py-2 font-mono text-sm dark:border-gray-600 dark:bg-gray-700" />
        </div>
      )}
      <div className="mt-4 flex gap-2">
        <button onClick={onCancel} className="flex-1 rounded border py-2 text-sm dark:border-gray-600">Cancel</button>
        <button onClick={onConfirm} disabled={!canConfirm}
          className={`flex-1 rounded py-2 text-sm font-semibold text-white disabled:opacity-40 ${bgColor}`}>
          {countdown > 0 ? `Wait ${countdown}s...` : `Confirm ${action}`}
        </button>
      </div>
    </div>
  );
}
