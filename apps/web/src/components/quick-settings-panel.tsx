"use client";

interface Setting { value: unknown; type: string; label: string; category: string;
  modified: boolean; options?: string[]; }
interface QuickSettingsPanelProps { settings: Record<string, Setting>; categories: string[];
  modifiedCount: number; onToggle: (key: string, value: unknown) => void; onReset: (key: string) => void; }

const catIcon: Record<string, string> = { general: "⚙️", appearance: "🎨", localization: "🌐", privacy: "🔒" };

export function QuickSettingsPanel({ settings, categories, modifiedCount, onToggle, onReset }: QuickSettingsPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Quick Settings</h2>
        {modifiedCount > 0 && <span className="text-xs text-blue-500">{modifiedCount} modified</span>}
      </div>
      {categories.map(cat => (
        <div key={cat}>
          <h3 className="flex items-center gap-1 text-xs font-medium uppercase text-gray-400">
            {catIcon[cat] ?? "📁"} {cat}
          </h3>
          <div className="mt-1 space-y-1.5">
            {Object.entries(settings).filter(([_, s]) => s.category === cat).map(([key, s]) => (
              <div key={key} className="flex items-center justify-between rounded-lg border px-4 py-2.5 dark:border-gray-700">
                <span className="text-sm">{s.label}</span>
                <div className="flex items-center gap-2">
                  {s.type === "boolean" ? (
                    <button onClick={() => onToggle(key, !s.value)}
                      className={`relative h-6 w-11 rounded-full ${s.value ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"}`}>
                      <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow ${s.value ? "left-[1.375rem]" : "left-0.5"}`} />
                    </button>
                  ) : (
                    <select value={String(s.value)} onChange={e => onToggle(key, e.target.value)}
                      className="rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-700">
                      {s.options?.map(o => <option key={o} value={o}>{o}</option>)}
                    </select>
                  )}
                  {s.modified && <button onClick={() => onReset(key)} className="text-xs text-blue-500">Reset</button>}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
