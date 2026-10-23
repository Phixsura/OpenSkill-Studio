"use client";

interface Setting { key: string; label: string; type: string; value: unknown; }
interface SettingGroup { id: string; label: string; icon: string; settings: Setting[]; }
interface OrgSettingsPageProps { groups: SettingGroup[]; orgName: string; onSave: () => void; }

export function OrgSettingsPage({ groups, orgName, onSave }: OrgSettingsPageProps) {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h2 className="text-lg font-bold">{orgName} Settings</h2>
      {groups.map(g => (
        <div key={g.id} className="rounded-xl border p-5 dark:border-gray-700">
          <h3 className="flex items-center gap-2 text-sm font-semibold mb-3">
            <span>{g.icon}</span>{g.label}
          </h3>
          <div className="space-y-3">
            {g.settings.map(s => (
              <div key={s.key} className="flex items-center justify-between">
                <label className="text-sm">{s.label}</label>
                {s.type === "toggle" ? (
                  <input type="checkbox" defaultChecked={!!s.value} className="accent-blue-600" />
                ) : s.type === "display" ? (
                  <span className="text-sm text-gray-500 capitalize">{String(s.value ?? "—")}</span>
                ) : (
                  <input type="text" defaultValue={String(s.value ?? "")}
                    className="rounded border px-2 py-1 text-sm dark:bg-gray-800 dark:border-gray-600 w-48" />
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
