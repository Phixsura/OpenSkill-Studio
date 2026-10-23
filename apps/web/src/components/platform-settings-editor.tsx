"use client";

interface SettingsSection { section: string; fields: Record<string, unknown>; }
interface PlatformSettingsEditorProps { sections: SettingsSection[];
  onSave: (settings: Record<string, unknown>) => void; }

export function PlatformSettingsEditor({ sections, onSave }: PlatformSettingsEditorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚙️ Platform Settings</h3>
        <button onClick={() => onSave({})}
          className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">Save</button>
      </div>
      {sections.map(s => (
        <div key={s.section} className="border-b last:border-0 dark:border-gray-700">
          <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800 text-xs font-semibold text-gray-400 uppercase">{s.section}</div>
          <div className="p-4 space-y-2">
            {Object.entries(s.fields).map(([key, val]) => (
              <div key={key} className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-300">{key.replace(/_/g, " ")}</span>
                <span className="font-mono text-xs text-gray-400">{String(val)}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
