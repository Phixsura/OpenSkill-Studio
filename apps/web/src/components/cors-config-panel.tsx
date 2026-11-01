"use client";

import { useState } from "react";

interface CorsConfigPanelProps {
  origins: string[]; methods: string[]; headers: string[];
  maxAgeS: number; credentials: boolean;
  onSave: (config: { origins: string[]; methods: string[]; credentials: boolean }) => void;
}

const allMethods = ["GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH", "DELETE"];

export function CorsConfigPanel({ origins, methods, headers, maxAgeS, credentials, onSave }: CorsConfigPanelProps) {
  const [newOrigin, setNewOrigin] = useState("");
  const [originList, setOriginList] = useState(origins);

  const addOrigin = () => {
    if (newOrigin && !originList.includes(newOrigin)) {
      setOriginList([...originList, newOrigin]);
      setNewOrigin("");
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">CORS Configuration</h3>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Allowed Origins</label>
        <div className="flex gap-2 mb-2">
          <input type="text" value={newOrigin} onChange={e => setNewOrigin(e.target.value)}
            placeholder="https://example.com" className="flex-1 rounded border px-3 py-1.5 text-sm dark:bg-gray-800 dark:border-gray-600" />
          <button onClick={addOrigin} className="rounded bg-blue-600 px-3 py-1.5 text-xs text-white">Add</button>
        </div>
        <div className="flex flex-wrap gap-1">
          {originList.map(o => (
            <span key={o} className="rounded bg-gray-100 px-2 py-0.5 text-xs font-mono dark:bg-gray-800">{o}
              <button onClick={() => setOriginList(originList.filter(x => x !== o))} className="ml-1 text-red-500">×</button>
            </span>
          ))}
        </div>
      </div>
      <div>
        <label className="block text-xs text-gray-400 mb-1">Methods</label>
        <div className="flex flex-wrap gap-1">
          {allMethods.map(m => (
            <span key={m} className={`rounded px-2 py-0.5 text-xs ${methods.includes(m) ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-gray-100 dark:bg-gray-800 text-gray-400"}`}>{m}</span>
          ))}
        </div>
      </div>
      <div className="flex items-center gap-4 text-sm">
        <span className="text-gray-400">Max Age: {maxAgeS}s</span>
        <span className={credentials ? "text-green-600" : "text-gray-400"}>Credentials: {credentials ? "Yes" : "No"}</span>
      </div>
      <button onClick={() => onSave({ origins: originList, methods, credentials })}
        className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Save CORS Config</button>
    </div>
  );
}
