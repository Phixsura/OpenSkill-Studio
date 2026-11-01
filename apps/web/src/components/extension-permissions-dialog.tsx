"use client";

import { useState } from "react";

interface Permission {
  key: string;
  label: string;
  description: string;
  level: "read" | "write" | "admin";
  required: boolean;
}

export function ExtensionPermissionsDialog({
  extensionName,
  permissions,
  onApprove,
  onDeny,
}: {
  extensionName: string;
  permissions: Permission[];
  onApprove?: (granted: string[]) => void;
  onDeny?: () => void;
}) {
  const [selected, setSelected] = useState<Set<string>>(
    new Set(permissions.filter((p) => p.required).map((p) => p.key))
  );

  const toggle = (key: string, required: boolean) => {
    if (required) return; // can't toggle required
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });
  };

  const levelColors: Record<string, string> = {
    read: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
    write: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300",
    admin: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300",
  };

  const allRequired = permissions.filter((p) => p.required).every((p) => selected.has(p.key));

  return (
    <div className="rounded-xl border dark:border-gray-700 p-6 max-w-md mx-auto space-y-5">
      <div className="text-center">
        <div className="text-3xl mb-2">🔐</div>
        <h2 className="text-lg font-bold">Permission Request</h2>
        <p className="text-sm text-gray-500">
          <strong>{extensionName}</strong> is requesting the following permissions:
        </p>
      </div>

      <div className="space-y-2">
        {permissions.map((perm) => (
          <label
            key={perm.key}
            className={`flex items-start gap-3 p-3 rounded-lg border dark:border-gray-700 cursor-pointer transition ${
              selected.has(perm.key) ? "bg-blue-50 dark:bg-blue-900/10 border-blue-300 dark:border-blue-700" : ""
            }`}
          >
            <input
              type="checkbox"
              checked={selected.has(perm.key)}
              onChange={() => toggle(perm.key, perm.required)}
              disabled={perm.required}
              className="mt-1"
            />
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm">{perm.label}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded ${levelColors[perm.level]}`}>
                  {perm.level}
                </span>
                {perm.required && (
                  <span className="text-xs text-red-500">required</span>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-0.5">{perm.description}</p>
            </div>
          </label>
        ))}
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => onDeny?.()}
          className="flex-1 rounded-lg border dark:border-gray-600 py-2 text-sm font-medium"
        >
          Deny
        </button>
        <button
          onClick={() => onApprove?.([...selected])}
          disabled={!allRequired}
          className="flex-1 rounded-lg bg-blue-600 text-white py-2 text-sm font-medium disabled:opacity-50"
        >
          Approve ({selected.size})
        </button>
      </div>
    </div>
  );
}
