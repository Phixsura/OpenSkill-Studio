"use client";

import { useState } from "react";

interface EnvVar { key: string; value: string; }
interface EnvVarEditorProps { vars: EnvVar[]; onChange: (vars: EnvVar[]) => void; }

export function EnvVarEditor({ vars, onChange }: EnvVarEditorProps) {
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");

  const add = () => {
    if (!key) return;
    onChange([...vars, { key: key.toUpperCase(), value }]);
    setKey(""); setValue("");
  };

  const remove = (idx: number) => onChange(vars.filter((_, i) => i !== idx));

  return (
    <div className="space-y-2">
      {vars.map((v, i) => (
        <div key={i} className="flex items-center gap-2 rounded bg-gray-100 px-2 py-1 text-sm dark:bg-gray-800">
          <code className="font-semibold">{v.key}</code>
          <span className="text-gray-400">=</span>
          <span className="flex-1 truncate text-gray-600">{v.value ? "••••••" : "(empty)"}</span>
          <button onClick={() => remove(i)} className="text-xs text-red-500">×</button>
        </div>
      ))}
      <div className="flex gap-2">
        <input value={key} onChange={e => setKey(e.target.value)} placeholder="KEY_NAME"
          className="w-1/3 rounded border px-2 py-1 text-sm font-mono dark:border-gray-600 dark:bg-gray-800" />
        <input value={value} onChange={e => setValue(e.target.value)} placeholder="value" type="password"
          className="flex-1 rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800" />
        <button onClick={add} disabled={!key} className="rounded bg-blue-600 px-3 py-1 text-sm text-white disabled:opacity-50">Add</button>
      </div>
    </div>
  );
}
