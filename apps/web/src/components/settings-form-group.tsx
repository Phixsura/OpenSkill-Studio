"use client";

interface Setting { key: string; type: string; label: string; required?: boolean; default?: unknown; }
interface SettingsFormGroupProps { group: string; icon: string; settings: Setting[]; values: Record<string, unknown>; onChange: (key: string, value: unknown) => void; }

export function SettingsFormGroup({ group, icon, settings, values, onChange }: SettingsFormGroupProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="flex items-center gap-2 font-semibold">
        <span>{icon}</span> {group}
      </h3>
      <div className="mt-3 space-y-3">
        {settings.map(s => (
          <div key={s.key}>
            <label className="block text-sm font-medium">{s.label} {s.required && <span className="text-red-500">*</span>}</label>
            {s.type === "boolean" ? (
              <input type="checkbox" checked={Boolean(values[s.key] ?? s.default)} onChange={e => onChange(s.key, e.target.checked)}
                className="mt-1" />
            ) : s.type === "integer" ? (
              <input type="number" value={Number(values[s.key] ?? s.default ?? 0)} onChange={e => onChange(s.key, Number(e.target.value))}
                className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
            ) : (
              <input type="text" value={String(values[s.key] ?? s.default ?? "")} onChange={e => onChange(s.key, e.target.value)}
                className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
