"use client";

interface ConfigFlag { key: string; value: unknown; description: string; type: string; owner: string; }
interface DynamicConfigEditorProps { flags: ConfigFlag[]; onUpdate: (key: string, value: unknown) => void; }

export function DynamicConfigEditor({ flags, onUpdate }: DynamicConfigEditorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🎛️ Dynamic Config</h3>
        <span className="text-xs text-gray-400">{flags.length} flags</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {flags.map(f => (
          <div key={f.key} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <div className="text-sm font-mono font-medium">{f.key}</div>
              <div className="text-[10px] text-gray-400">{f.description} · {f.owner}</div>
            </div>
            <div className="flex items-center gap-2">
              {f.type === "bool" ? (
                <button onClick={() => onUpdate(f.key, !f.value)}
                  className={`w-8 h-4 rounded-full ${f.value ? "bg-green-500" : "bg-gray-300"}`}>
                  <span className={`block w-3 h-3 rounded-full bg-white transform ${f.value ? "translate-x-4" : "translate-x-0.5"}`} />
                </button>
              ) : (
                <span className="text-xs font-mono text-gray-400">{String(f.value)}</span>
              )}
              <span className="text-[10px] text-gray-300">{f.type}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
