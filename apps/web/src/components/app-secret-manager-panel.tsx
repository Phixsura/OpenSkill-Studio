"use client";

import { useState } from "react";

interface SecretMeta {
  key: string;
  version: number;
  created_at: string;
  updated_at: string;
  expires_at: string | null;
  has_previous: boolean;
  value_hash: string;
}

interface AppSecretManagerPanelProps {
  installationId: string;
  secrets: SecretMeta[];
  maxSecrets: number;
  onAdd: (key: string, value: string) => void;
  onRotate: (key: string) => void;
  onDelete: (key: string) => void;
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

export function AppSecretManagerPanel({
  secrets,
  maxSecrets,
  onAdd,
  onRotate,
  onDelete,
}: AppSecretManagerPanelProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");
  const atLimit = secrets.length >= maxSecrets;

  function handleAdd() {
    if (newKey.trim() && newValue.trim()) {
      onAdd(newKey.trim(), newValue.trim());
      setNewKey("");
      setNewValue("");
      setShowAddForm(false);
    }
  }

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div>
          <h3 className="font-semibold">Secrets</h3>
          <p className="text-xs text-gray-500">
            {secrets.length}/{maxSecrets} secrets used
          </p>
        </div>
        {!atLimit && (
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700"
          >
            {showAddForm ? "Cancel" : "+ Add Secret"}
          </button>
        )}
        {atLimit && <span className="text-xs text-red-600">Limit reached</span>}
      </div>

      {/* Add form */}
      {showAddForm && (
        <div className="border-b border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-800/30">
          <div className="space-y-2">
            <input
              type="text"
              value={newKey}
              onChange={(e) => setNewKey(e.target.value)}
              placeholder="SECRET_KEY"
              className="block w-full rounded border border-gray-300 px-2 py-1.5 font-mono text-sm dark:border-gray-600 dark:bg-gray-800"
              aria-label="Secret key"
            />
            <input
              type="password"
              value={newValue}
              onChange={(e) => setNewValue(e.target.value)}
              placeholder="Secret value"
              className="block w-full rounded border border-gray-300 px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800"
              aria-label="Secret value"
            />
            <button
              onClick={handleAdd}
              disabled={!newKey.trim() || !newValue.trim()}
              className="rounded bg-green-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-green-700 disabled:opacity-50"
            >
              Save Secret
            </button>
          </div>
        </div>
      )}

      {/* Secret list */}
      {secrets.length === 0 ? (
        <div className="py-8 text-center">
          <span className="text-3xl">🔐</span>
          <p className="mt-2 text-sm text-gray-500">No secrets stored</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {secrets.map((s) => (
            <div key={s.key} className="flex items-center justify-between px-4 py-2.5">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <code className="text-sm font-medium">{s.key}</code>
                  <span className="rounded bg-gray-100 px-1 py-0.5 text-[10px] text-gray-500 dark:bg-gray-800">
                    v{s.version}
                  </span>
                  {s.has_previous && (
                    <span className="rounded bg-yellow-100 px-1 py-0.5 text-[10px] text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300">
                      rotating
                    </span>
                  )}
                  {s.expires_at && (
                    <span className="text-[10px] text-gray-400">
                      expires {formatDate(s.expires_at)}
                    </span>
                  )}
                </div>
                <p className="text-[10px] text-gray-400">
                  Updated {formatDate(s.updated_at)} • hash: {s.value_hash}
                </p>
              </div>
              <div className="flex gap-1.5">
                <button
                  onClick={() => onRotate(s.key)}
                  className="rounded border border-blue-300 px-2 py-1 text-[10px] text-blue-600 hover:bg-blue-50 dark:border-blue-700 dark:text-blue-400"
                >
                  Rotate
                </button>
                <button
                  onClick={() => onDelete(s.key)}
                  className="rounded border border-red-300 px-2 py-1 text-[10px] text-red-600 hover:bg-red-50 dark:border-red-700 dark:text-red-400"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
