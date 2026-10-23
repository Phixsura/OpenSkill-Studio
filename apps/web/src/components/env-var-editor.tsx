"use client";

import { useState } from "react";

interface EnvVar { key: string; value: string; is_sensitive: boolean; source: string; }
interface EnvVarEditorProps { variables: EnvVar[]; onDelete: (key: string) => void; }

export function EnvVarEditor({ variables, onDelete }: EnvVarEditorProps) {
  const [revealed, setRevealed] = useState<Set<string>>(new Set());
  const toggle = (key: string) => {
    const next = new Set(revealed);
    next.has(key) ? next.delete(key) : next.add(key);
    setRevealed(next);
  };

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold">Environment Variables</h3>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {variables.map(v => (
          <div key={v.key} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-3 min-w-0">
              <code className="text-sm font-mono font-medium">{v.key}</code>
              {v.is_sensitive && !revealed.has(v.key)
                ? <span className="text-sm text-gray-400">••••••••</span>
                : <span className="text-sm text-gray-500 truncate max-w-[200px]">{v.value}</span>}
            </div>
            <div className="flex items-center gap-2">
              {v.is_sensitive && (
                <button onClick={() => toggle(v.key)} className="text-xs text-blue-600 hover:underline">
                  {revealed.has(v.key) ? "Hide" : "Reveal"}
                </button>
              )}
              <button onClick={() => onDelete(v.key)} className="text-xs text-red-600 hover:underline">Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
