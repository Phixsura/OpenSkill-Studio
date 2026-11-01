"use client";

import { useState } from "react";

interface ExportImportDialogProps { mode: "export" | "import";
  sections: string[]; onExport: (sections: string[]) => void;
  onImport: (data: string) => void; onClose: () => void; }

export function ExportImportDialog({ mode, sections, onExport, onImport, onClose }: ExportImportDialogProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set(sections));
  const [importData, setImportData] = useState("");

  const toggle = (s: string) => {
    const next = new Set(selected);
    next.has(s) ? next.delete(s) : next.add(s);
    setSelected(next);
  };

  return (
    <div className="rounded-lg border bg-white p-5 shadow-lg dark:border-gray-700 dark:bg-gray-900">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{mode === "export" ? "Export" : "Import"} Config</h2>
        <button onClick={onClose} className="text-gray-400">✕</button>
      </div>
      {mode === "export" ? (
        <div className="mt-4 space-y-2">
          {sections.map(s => (
            <label key={s} className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={selected.has(s)} onChange={() => toggle(s)} className="accent-blue-600" />
              <span className="capitalize">{s.replace(/_/g, " ")}</span>
            </label>
          ))}
          <button onClick={() => onExport([...selected])}
            className="mt-3 w-full rounded bg-blue-600 py-2 text-sm text-white">Export Selected</button>
        </div>
      ) : (
        <div className="mt-4 space-y-3">
          <textarea value={importData} onChange={e => setImportData(e.target.value)}
            placeholder="Paste exported JSON..." rows={5}
            className="w-full rounded border px-3 py-2 font-mono text-xs dark:border-gray-600 dark:bg-gray-700" />
          <button onClick={() => onImport(importData)}
            className="w-full rounded bg-green-600 py-2 text-sm text-white">Import</button>
        </div>
      )}
    </div>
  );
}
