"use client";

interface ConfigEntry { key: string; value: unknown; type: string; hasDefault: boolean; }
interface RuntimeConfigEditorProps { entries: ConfigEntry[]; errors: { key: string; error: string }[];
  onSave: (config: Record<string, unknown>) => void; }

export function RuntimeConfigEditor({ entries, errors, onSave }: RuntimeConfigEditorProps) {
  const errorMap = Object.fromEntries(errors.map(e => [e.key, e.error]));
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Runtime Configuration</h3>
      <div className="space-y-3">
        {entries.map(e => (
          <div key={e.key}>
            <div className="flex items-center gap-2">
              <label className="text-sm font-mono font-medium">{e.key}</label>
              <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{e.type}</span>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">Current: {JSON.stringify(e.value)}</p>
            {errorMap[e.key] && <p className="text-xs text-red-500 mt-0.5">⚠ {errorMap[e.key]}</p>}
          </div>
        ))}
      </div>
      <button onClick={() => onSave(Object.fromEntries(entries.map(e => [e.key, e.value])))}
        className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Save Config</button>
    </div>
  );
}
