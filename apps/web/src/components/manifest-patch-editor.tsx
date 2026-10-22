"use client";

import { useState } from "react";

interface Patch { op: string; path: string; value?: unknown; }

interface ManifestPatchEditorProps {
  onApply: (patches: Patch[]) => void;
}

export function ManifestPatchEditor({ onApply }: ManifestPatchEditorProps) {
  const [patches, setPatches] = useState<Patch[]>([]);
  const [path, setPath] = useState("");
  const [value, setValue] = useState("");
  const [op, setOp] = useState("set");

  const addPatch = () => {
    if (!path) return;
    const p: Patch = { op, path };
    if (op !== "delete") {
      try { p.value = JSON.parse(value); } catch { p.value = value; }
    }
    setPatches([...patches, p]);
    setPath(""); setValue("");
  };

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <select value={op} onChange={e => setOp(e.target.value)} className="rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800">
          <option value="set">Set</option>
          <option value="delete">Delete</option>
          <option value="append">Append</option>
        </select>
        <input value={path} onChange={e => setPath(e.target.value)} placeholder="path.to.field"
          className="flex-1 rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800" />
        {op !== "delete" && (
          <input value={value} onChange={e => setValue(e.target.value)} placeholder="value"
            className="flex-1 rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800" />
        )}
        <button onClick={addPatch} className="rounded bg-blue-600 px-3 py-1 text-sm text-white">Add</button>
      </div>
      {patches.length > 0 && (
        <div className="space-y-1">
          {patches.map((p, i) => (
            <div key={i} className="flex items-center gap-2 rounded bg-gray-100 px-2 py-1 text-xs dark:bg-gray-800">
              <span className="font-medium">{p.op}</span>
              <span className="font-mono">{p.path}</span>
              {p.value !== undefined && <span className="text-gray-500">= {JSON.stringify(p.value)}</span>}
              <button onClick={() => setPatches(patches.filter((_, j) => j !== i))} className="ml-auto text-red-500">×</button>
            </div>
          ))}
          <button onClick={() => onApply(patches)} className="rounded bg-green-600 px-4 py-1 text-sm text-white">Apply {patches.length} patches</button>
        </div>
      )}
    </div>
  );
}
