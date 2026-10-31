"use client";

import { useState } from "react";

interface TransferDialogProps { appName: string; onSubmit: (targetDevId: string, reason: string) => void; onCancel: () => void; }

export function TransferDialog({ appName, onSubmit, onCancel }: TransferDialogProps) {
  const [targetId, setTargetId] = useState("");
  const [reason, setReason] = useState("");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" role="dialog" aria-label="Transfer app">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
        <h2 className="text-lg font-semibold">Transfer {appName}</h2>
        <p className="mt-1 text-sm text-gray-500">Transfer ownership to another developer account.</p>
        <div className="mt-4 space-y-3">
          <div>
            <label className="block text-sm font-medium">Developer ID</label>
            <input value={targetId} onChange={e => setTargetId(e.target.value)}
              placeholder="Enter developer account ID" className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
          </div>
          <div>
            <label className="block text-sm font-medium">Reason</label>
            <input value={reason} onChange={e => setReason(e.target.value)}
              placeholder="Why are you transferring?" className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
          </div>
        </div>
        <div className="mt-6 flex justify-end gap-3">
          <button onClick={onCancel} className="rounded px-4 py-2 text-sm text-gray-600">Cancel</button>
          <button onClick={() => onSubmit(targetId, reason)} disabled={!targetId}
            className="rounded bg-orange-600 px-4 py-2 text-sm text-white hover:bg-orange-700 disabled:opacity-50">Transfer</button>
        </div>
      </div>
    </div>
  );
}
