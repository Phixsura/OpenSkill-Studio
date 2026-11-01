"use client";

import { useState } from "react";

interface ApiKeyDisplayProps {
  keyPrefix: string;
  name: string;
  rawKey?: string;
  scopes: string[];
  createdAt: string;
  onRevoke?: () => void;
}

export function ApiKeyDisplay({ keyPrefix, name, rawKey, scopes, createdAt, onRevoke }: ApiKeyDisplayProps) {
  const [copied, setCopied] = useState(false);

  const copyKey = () => {
    if (rawKey) {
      navigator.clipboard?.writeText(rawKey);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-2 flex items-center justify-between">
        <h4 className="font-semibold">{name}</h4>
        {onRevoke && (
          <button onClick={onRevoke} className="text-xs text-red-500 hover:text-red-700">Revoke</button>
        )}
      </div>
      <div className="mb-2 flex items-center gap-2">
        <code className="rounded bg-gray-100 px-2 py-1 text-sm dark:bg-gray-800">
          {rawKey ?? `${keyPrefix}${"•".repeat(24)}`}
        </code>
        {rawKey && (
          <button onClick={copyKey} className="text-xs text-blue-600">{copied ? "Copied!" : "Copy"}</button>
        )}
      </div>
      {rawKey && (
        <p className="mb-2 text-xs text-yellow-600 dark:text-yellow-400">
          ⚠️ Save this key now — it won&apos;t be shown again
        </p>
      )}
      <div className="flex flex-wrap gap-1">
        {scopes.map(s => (
          <span key={s} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{s}</span>
        ))}
      </div>
      <p className="mt-2 text-xs text-gray-400">Created {createdAt}</p>
    </div>
  );
}
