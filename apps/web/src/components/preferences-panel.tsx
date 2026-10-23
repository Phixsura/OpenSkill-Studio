"use client";

interface PreferenceSetting { key: string; label: string; type: string; options?: (string | number)[]; }
interface PreferencesPanelProps { settings: PreferenceSetting[]; values: Record<string, unknown>; onChange: (key: string, value: unknown) => void; onReset: () => void; }

export function PreferencesPanel({ settings, values, onChange, onReset }: PreferencesPanelProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Preferences</h3>
        <button onClick={onReset} className="text-xs text-gray-400 hover:text-gray-600">Reset to defaults</button>
      </div>
      <div className="mt-3 space-y-3">
        {settings.map(s => (
          <div key={s.key} className="flex items-center justify-between">
            <label className="text-sm">{s.label}</label>
            {s.type === "select" && s.options && (
              <select value={String(values[s.key] || "")} onChange={e => onChange(s.key, e.target.value)}
                className="rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-700">
                {s.options.map(o => <option key={String(o)} value={String(o)}>{String(o)}</option>)}
              </select>
            )}
            {s.type === "boolean" && (
              <input type="checkbox" checked={Boolean(values[s.key])} onChange={e => onChange(s.key, e.target.checked)} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
