"use client";

import { useState } from "react";

interface CorsConfigEditorProps { origins: string[]; methods: string[]; maxAgeSec: number;
  onSave: (origins: string[], methods: string[], maxAge: number) => void; }

const ALL_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"];

export function CorsConfigEditor({ origins, methods, maxAgeSec, onSave }: CorsConfigEditorProps) {
  const [newOrigin, setNewOrigin] = useState("");
  const [localOrigins, setLocalOrigins] = useState(origins);
  const [localMethods, setLocalMethods] = useState(new Set(methods));

  const addOrigin = () => {
    if (newOrigin && !localOrigins.includes(newOrigin)) {
      setLocalOrigins([...localOrigins, newOrigin]);
      setNewOrigin("");
    }
  };

  const toggleMethod = (m: string) => {
    const next = new Set(localMethods);
    next.has(m) ? next.delete(m) : next.add(m);
    setLocalMethods(next);
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">CORS Configuration</h2>
      <div>
        <h3 className="text-sm font-medium">Allowed Origins</h3>
        <div className="mt-1 flex gap-2">
          <input value={newOrigin} onChange={e => setNewOrigin(e.target.value)}
            placeholder="https://example.com" className="flex-1 rounded border px-3 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-700" />
          <button onClick={addOrigin} className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white">Add</button>
        </div>
        <div className="mt-2 flex flex-wrap gap-1">
          {localOrigins.map(o => (
            <span key={o} className="flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs dark:border-gray-600">
              {o}
              <button onClick={() => setLocalOrigins(localOrigins.filter(x => x !== o))} className="text-red-400">×</button>
            </span>
          ))}
        </div>
      </div>
      <div>
        <h3 className="text-sm font-medium">Allowed Methods</h3>
        <div className="mt-1 flex flex-wrap gap-2">
          {ALL_METHODS.map(m => (
            <label key={m} className="flex items-center gap-1 text-sm">
              <input type="checkbox" checked={localMethods.has(m)} onChange={() => toggleMethod(m)} className="accent-blue-600" />
              {m}
            </label>
          ))}
        </div>
      </div>
      <button onClick={() => onSave(localOrigins, [...localMethods], maxAgeSec)}
        className="w-full rounded bg-blue-600 py-2 text-sm text-white">Save CORS Config</button>
    </div>
  );
}
