"use client";

interface UserPrefsFormProps { prefs: Record<string, unknown>;
  onUpdate: (key: string, value: unknown) => void; onReset: () => void; }

export function UserPrefsForm({ prefs, onUpdate, onReset }: UserPrefsFormProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700 max-w-md">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">👤 Preferences</h3>
        <button onClick={onReset} className="text-xs text-gray-400 hover:text-red-500">Reset defaults</button>
      </div>
      <div className="space-y-3">
        {Object.entries(prefs).map(([key, val]) => (
          <div key={key} className="flex items-center justify-between">
            <span className="text-sm capitalize">{key.replace(/_/g, " ")}</span>
            {typeof val === "boolean" ? (
              <button onClick={() => onUpdate(key, !val)}
                className={`w-9 h-5 rounded-full ${val ? "bg-blue-500" : "bg-gray-300"}`}>
                <span className={`block w-4 h-4 rounded-full bg-white transform ${val ? "translate-x-4" : "translate-x-0.5"}`} />
              </button>
            ) : (
              <span className="text-xs font-mono text-gray-400">{String(val)}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
