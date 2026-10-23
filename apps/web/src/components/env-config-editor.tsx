"use client";

import { useState } from "react";

interface EnvVar { key: string; display_value: string; is_secret: boolean; }
interface EnvConfigEditorProps { variables: EnvVar[]; onSave: (key: string, value: string, isSecret: boolean) => void;
  onDelete: (key: string) => void; }

export function EnvConfigEditor({ variables, onSave, onDelete }: EnvConfigEditorProps) {
  const [newKey, setNewKey] = useState("");
  const [newVal, setNewVal] = useState("");
  const [isSecret, setIsSecret] = useState(false);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Environment Variables</h2>
      <div className="space-y-2">
        {variables.map(v => (
          <div key={v.key} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm font-medium">{v.key}</span>
              {v.is_secret && <span className="rounded bg-yellow-100 px-1 py-0.5 text-[10px] text-yellow-700 dark:bg-yellow-900/30">SECRET</span>}
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-gray-400">{v.display_value}</span>
              <button onClick={() => onDelete(v.key)} className="text-xs text-red-500">×</button>
            </div>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input value={newKey} onChange={e => setNewKey(e.target.value)} placeholder="KEY"
          className="w-32 rounded border px-2 py-1.5 font-mono text-sm dark:border-gray-600 dark:bg-gray-700" />
        <input value={newVal} onChange={e => setNewVal(e.target.value)} placeholder="value"
          type={isSecret ? "password" : "text"}
          className="flex-1 rounded border px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <label className="flex items-center gap-1 text-xs"><input type="checkbox" checked={isSecret} onChange={e => setIsSecret(e.target.checked)} />Secret</label>
        <button onClick={() => { onSave(newKey, newVal, isSecret); setNewKey(""); setNewVal(""); }}
          className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Add</button>
      </div>
    </div>
  );
}
