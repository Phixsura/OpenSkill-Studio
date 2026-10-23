"use client";
import { useState } from "react";

interface EnvVar { key: string; masked: string; sensitive: boolean; }
interface EnvVarEditorProps { vars: EnvVar[]; onAdd: (key: string, value: string, sensitive: boolean) => void; }

export function EnvVarEditor({ vars, onAdd }: EnvVarEditorProps) {
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");
  const [sensitive, setSensitive] = useState(true);

  const handleAdd = () => {
    if (key.trim()) { onAdd(key.trim(), value, sensitive); setKey(""); setValue(""); }
  };

  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔐 Environment Variables</h3>
      <div className="space-y-2 mb-4">
        {vars.map(v => (
          <div key={v.key} className="flex items-center justify-between text-sm bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
            <span className="font-mono text-xs">{v.key}</span>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-gray-400">{v.masked}</span>
              {v.sensitive && <span className="text-xs text-yellow-500">🔒</span>}
            </div>
          </div>
        ))}
        {vars.length === 0 && <p className="text-sm text-gray-400">No variables set</p>}
      </div>
      <div className="flex gap-2">
        <input placeholder="KEY" value={key} onChange={e => setKey(e.target.value)}
          className="flex-1 text-sm px-2 py-1.5 border rounded dark:bg-gray-800 dark:border-gray-600 font-mono" />
        <input placeholder="value" value={value} onChange={e => setValue(e.target.value)}
          type={sensitive ? "password" : "text"}
          className="flex-1 text-sm px-2 py-1.5 border rounded dark:bg-gray-800 dark:border-gray-600" />
        <label className="flex items-center gap-1 text-xs">
          <input type="checkbox" checked={sensitive} onChange={e => setSensitive(e.target.checked)} />
          Secret
        </label>
        <button onClick={handleAdd}
          className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">Add</button>
      </div>
    </div>
  );
}
