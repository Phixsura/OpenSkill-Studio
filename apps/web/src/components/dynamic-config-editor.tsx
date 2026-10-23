"use client";

interface ConfigEntry { key: string; value: unknown; value_type: string; description: string; environment: string; updated_at: string; }
interface DynamicConfigEditorProps { configs: ConfigEntry[]; environment: string;
  onUpdate: (key: string, value: string) => void; onDelete: (key: string) => void; }

const typeIcon: Record<string, string> = { string: "📝", number: "🔢", boolean: "✅", json: "📋" };

export function DynamicConfigEditor({ configs, environment, onUpdate, onDelete }: DynamicConfigEditorProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Dynamic Config</h2>
        <span className="rounded bg-gray-100 px-2 py-0.5 text-xs capitalize dark:bg-gray-800">{environment}</span>
      </div>
      {configs.map(c => (
        <div key={c.key} className="flex items-center justify-between rounded-lg border px-4 py-2.5 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <span>{typeIcon[c.value_type] ?? "⚙️"}</span>
            <div>
              <p className="font-mono text-sm font-medium">{c.key}</p>
              {c.description && <p className="text-xs text-gray-400">{c.description}</p>}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-sm text-blue-600">{String(c.value)}</span>
            <button onClick={() => onDelete(c.key)} className="text-xs text-red-400">×</button>
          </div>
        </div>
      ))}
      {configs.length === 0 && <p className="text-center text-sm text-gray-400">No config entries</p>}
    </div>
  );
}
