"use client";

interface Preference { value: unknown; options: unknown[] | null; category: string; is_default: boolean; }
interface UserPreferencesPageProps { preferences: Record<string, Preference>; categories: string[];
  onUpdate: (key: string, value: unknown) => void; onReset: (key: string) => void; }

const catIcons: Record<string, string> = {
  appearance: "🎨", localization: "🌐", notifications: "🔔", editor: "✏️",
};

export function UserPreferencesPage({ preferences, categories, onUpdate, onReset }: UserPreferencesPageProps) {
  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">Preferences</h2>
      {categories.map(cat => (
        <div key={cat}>
          <h3 className="flex items-center gap-1.5 text-sm font-medium capitalize text-gray-500">
            <span>{catIcons[cat] ?? "⚙️"}</span> {cat}
          </h3>
          <div className="mt-2 space-y-2">
            {Object.entries(preferences)
              .filter(([_, p]) => p.category === cat)
              .map(([key, pref]) => (
                <div key={key} className="flex items-center justify-between rounded-lg border px-4 py-2.5 dark:border-gray-700">
                  <span className="text-sm capitalize">{key.replace(/_/g, " ")}</span>
                  <div className="flex items-center gap-2">
                    {pref.options && Array.isArray(pref.options) ? (
                      <select value={String(pref.value)} onChange={e => {
                        const v = e.target.value;
                        onUpdate(key, v === "true" ? true : v === "false" ? false : isNaN(Number(v)) ? v : Number(v));
                      }} className="rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-700">
                        {pref.options.map(o => <option key={String(o)} value={String(o)}>{String(o)}</option>)}
                      </select>
                    ) : (
                      <span className="text-sm text-gray-400">{String(pref.value)}</span>
                    )}
                    {!pref.is_default && (
                      <button onClick={() => onReset(key)} className="text-xs text-blue-500">Reset</button>
                    )}
                  </div>
                </div>
              ))}
          </div>
        </div>
      ))}
    </div>
  );
}
