"use client";

interface UserPrefsFormProps { preferences: Record<string, unknown>; customized: number;
  onSet: (key: string, value: unknown) => void; onReset: () => void; }

export function UserPrefsForm({ preferences, customized, onSet, onReset }: UserPrefsFormProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚙️ Preferences</h3>
        <div className="flex gap-2">
          <span className="text-xs text-gray-400">{customized} customized</span>
          <button onClick={onReset} className="text-xs text-red-500 hover:underline">Reset</button>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {Object.entries(preferences).map(([k, v]) => (
          <div key={k} className="flex items-center justify-between px-4 py-2.5">
            <span className="text-sm">{k.replaceAll("_", " ")}</span>
            {typeof v === "boolean" ? (
              <button onClick={() => onSet(k, !v)}
                className={`w-8 h-4 rounded-full ${v ? "bg-blue-500" : "bg-gray-300"}`}>
                <span className={`block w-3 h-3 rounded-full bg-white transform ${v ? "translate-x-4" : "translate-x-0.5"}`} />
              </button>
            ) : (
              <span className="text-xs text-gray-400 font-mono">{String(v)}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
