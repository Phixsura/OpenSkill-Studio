"use client";
import { useState } from "react";

interface CorsConfigEditorProps { origins: string[]; methods: string[];
  headers: string[]; credentials: boolean;
  onAddOrigin: (origin: string) => void; onRemoveOrigin: (origin: string) => void; }

export function CorsConfigEditor({ origins, methods, headers, credentials, onAddOrigin, onRemoveOrigin }: CorsConfigEditorProps) {
  const [newOrigin, setNewOrigin] = useState("");
  const handleAdd = () => { if (newOrigin.trim()) { onAddOrigin(newOrigin.trim()); setNewOrigin(""); } };
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🌐 CORS Policy</h3>
      <div className="mb-4">
        <label className="block text-xs font-medium text-gray-400 mb-1">Allowed Origins</label>
        <div className="space-y-1 mb-2">
          {origins.map(o => (
            <div key={o} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded px-3 py-1.5 text-sm">
              <span className="font-mono text-xs">{o}</span>
              <button onClick={() => onRemoveOrigin(o)} className="text-xs text-red-500 hover:text-red-700">×</button>
            </div>
          ))}
        </div>
        <div className="flex gap-2">
          <input value={newOrigin} onChange={e => setNewOrigin(e.target.value)}
            placeholder="https://example.com"
            className="flex-1 text-sm px-2 py-1.5 border rounded font-mono dark:bg-gray-800 dark:border-gray-600" />
          <button onClick={handleAdd} className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700">Add</button>
        </div>
      </div>
      <div className="flex gap-4 text-xs text-gray-400">
        <span>Methods: {methods.join(", ")}</span>
        <span>Credentials: {credentials ? "✅" : "❌"}</span>
      </div>
    </div>
  );
}
