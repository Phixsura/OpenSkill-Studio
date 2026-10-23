"use client";

interface SettingsField { key: string; label: string; type: string; value: unknown; required?: boolean; }
interface SettingsSection { id: string; label: string; icon: string; fields: SettingsField[]; }
interface AppSettingsPageProps { sections: SettingsSection[]; appName: string; onSave: () => void; }

export function AppSettingsPage({ sections, appName, onSave }: AppSettingsPageProps) {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h2 className="text-lg font-bold">{appName} Settings</h2>
      {sections.map(sec => (
        <div key={sec.id} className={`rounded-xl border p-5 ${sec.id === "danger" ? "border-red-300 dark:border-red-700" : "dark:border-gray-700"}`}>
          <h3 className="flex items-center gap-2 text-sm font-semibold mb-3">
            <span>{sec.icon}</span>{sec.label}
          </h3>
          <div className="space-y-3">
            {sec.fields.map(f => (
              <div key={f.key}>
                <label className="block text-xs text-gray-400 mb-1">{f.label}{f.required && <span className="text-red-500"> *</span>}</label>
                {f.type === "toggle" ? (
                  <input type="checkbox" defaultChecked={!!f.value} className="accent-blue-600" />
                ) : f.type === "action_danger" ? (
                  <button className="rounded border border-red-300 px-3 py-1.5 text-xs text-red-600 dark:border-red-700">{f.label}</button>
                ) : f.type === "action" ? (
                  <button className="rounded border px-3 py-1.5 text-xs dark:border-gray-700">{f.label}</button>
                ) : (
                  <input type="text" defaultValue={String(f.value ?? "")}
                    className="w-full rounded border px-3 py-1.5 text-sm dark:bg-gray-800 dark:border-gray-600" />
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
      <button onClick={onSave} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Save Settings</button>
    </div>
  );
}
