"use client";

import { useState } from "react";

interface TransferOwnershipProps { appName: string; currentOrg: string;
  onTransfer: (toOrg: string) => void; onCancel: () => void; }

export function TransferOwnership({ appName, currentOrg, onTransfer, onCancel }: TransferOwnershipProps) {
  const [targetOrg, setTargetOrg] = useState("");
  const [confirmed, setConfirmed] = useState(false);

  return (
    <div className="mx-auto max-w-md space-y-4">
      <h2 className="text-lg font-bold">Transfer {appName}</h2>
      <p className="text-sm text-gray-500">Transfer ownership from <strong>{currentOrg}</strong> to another organization.</p>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Target Organization</label>
        <input value={targetOrg} onChange={e => setTargetOrg(e.target.value)}
          placeholder="Organization name or ID"
          className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      </div>
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} className="accent-blue-600" />
        I understand this will transfer all app data and settings
      </label>
      <div className="flex gap-3">
        <button onClick={onCancel} className="flex-1 rounded border py-2 text-sm dark:border-gray-700">Cancel</button>
        <button onClick={() => targetOrg && confirmed && onTransfer(targetOrg)}
          disabled={!targetOrg || !confirmed}
          className="flex-1 rounded bg-blue-600 py-2 text-sm text-white disabled:opacity-30">Transfer</button>
      </div>
    </div>
  );
}
