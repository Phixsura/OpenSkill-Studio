"use client";

interface UserPreferencesFormProps { preferences: Record<string, unknown>;
  availableThemes: string[]; availableLanguages: string[];
  onChange: (key: string, value: unknown) => void; }

export function UserPreferencesForm({ preferences, availableThemes, availableLanguages, onChange }: UserPreferencesFormProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Preferences</h3>
      <div className="space-y-3">
        <div>
          <label className="block text-xs text-gray-400 mb-1">Theme</label>
          <select value={String(preferences.theme)} onChange={e => onChange("theme", e.target.value)}
            className="w-full rounded border px-3 py-1.5 text-sm dark:bg-gray-800 dark:border-gray-600">
            {availableThemes.map(t => <option key={t}>{t}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-400 mb-1">Language</label>
          <select value={String(preferences.language)} onChange={e => onChange("language", e.target.value)}
            className="w-full rounded border px-3 py-1.5 text-sm dark:bg-gray-800 dark:border-gray-600">
            {availableLanguages.map(l => <option key={l}>{l}</option>)}
          </select>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm">Email Notifications</span>
          <input type="checkbox" checked={!!preferences.notifications_email}
            onChange={e => onChange("notifications_email", e.target.checked)} className="accent-blue-600" />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm">Compact View</span>
          <input type="checkbox" checked={!!preferences.compact_view}
            onChange={e => onChange("compact_view", e.target.checked)} className="accent-blue-600" />
        </div>
      </div>
    </div>
  );
}
