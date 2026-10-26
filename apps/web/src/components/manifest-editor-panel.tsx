"use client";

import { useState } from "react";

interface ManifestData {
  name: string;
  version: string;
  manifestVersion: string;
  entrypoint: string;
  runtime: string;
  sdkVersion: string;
  permissions: string[];
  description: string;
  author: string;
  dependencies: Record<string, string>;
}

interface ValidationError {
  message: string;
}

const runtimes = ["node18", "node20", "python3.11", "python3.12", "deno", "bun"];

export function ManifestEditorPanel({
  manifest,
  errors,
  onSave,
  onValidate,
}: {
  manifest: ManifestData;
  errors: ValidationError[];
  onSave?: (m: ManifestData) => void;
  onValidate?: () => void;
}) {
  const [data, setData] = useState(manifest);
  const [newPerm, setNewPerm] = useState("");

  const update = (key: keyof ManifestData, value: string) => {
    setData((prev) => ({ ...prev, [key]: value }));
  };

  const addPermission = () => {
    if (newPerm.trim() && !data.permissions.includes(newPerm.trim())) {
      setData((prev) => ({ ...prev, permissions: [...prev.permissions, newPerm.trim()] }));
      setNewPerm("");
    }
  };

  const removePermission = (p: string) => {
    setData((prev) => ({ ...prev, permissions: prev.permissions.filter((x) => x !== p) }));
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📦 Manifest Editor</h2>
        <div className="flex gap-2">
          <button onClick={onValidate} className="text-sm bg-yellow-600 text-white px-3 py-1.5 rounded-lg">Validate</button>
          <button onClick={() => onSave?.(data)} className="text-sm bg-green-600 text-white px-3 py-1.5 rounded-lg">Save</button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-gray-500 block mb-0.5">Name</label>
          <input type="text" value={data.name} onChange={(e) => update("name", e.target.value)}
            className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm" />
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-0.5">Version</label>
          <input type="text" value={data.version} onChange={(e) => update("version", e.target.value)}
            className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm font-mono" />
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-0.5">Runtime</label>
          <select value={data.runtime} onChange={(e) => update("runtime", e.target.value)}
            className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm">
            {runtimes.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-0.5">Entrypoint</label>
          <input type="text" value={data.entrypoint} onChange={(e) => update("entrypoint", e.target.value)}
            className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-1.5 text-sm font-mono" />
        </div>
      </div>

      <div>
        <label className="text-xs text-gray-500 block mb-0.5">Permissions</label>
        <div className="flex flex-wrap gap-1 mb-1">
          {data.permissions.map((p) => (
            <span key={p} className="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded-full flex items-center gap-1">
              {p} <button onClick={() => removePermission(p)} className="text-blue-400 hover:text-red-500">×</button>
            </span>
          ))}
        </div>
        <div className="flex gap-1">
          <input type="text" value={newPerm} onChange={(e) => setNewPerm(e.target.value)}
            placeholder="permission:scope" className="flex-1 rounded border dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-xs" />
          <button onClick={addPermission} className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Add</button>
        </div>
      </div>

      {errors.length > 0 && (
        <div className="rounded-lg border border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/10 p-3 space-y-1">
          {errors.map((e, i) => (
            <div key={i} className="text-xs text-red-600">⚠ {e.message}</div>
          ))}
        </div>
      )}
    </div>
  );
}
