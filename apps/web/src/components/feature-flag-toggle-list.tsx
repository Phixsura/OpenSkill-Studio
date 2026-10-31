"use client";

interface Flag { name: string; description: string; enabled: boolean; rollout: number; }
interface FeatureFlagToggleListProps { flags: Flag[]; onToggle: (name: string, enabled: boolean) => void; }

export function FeatureFlagToggleList({ flags, onToggle }: FeatureFlagToggleListProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Feature Flags</h2>
      {flags.map(f => (
        <div key={f.name} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm font-medium">{f.name}</span>
              <span className={`rounded-full px-2 py-0.5 text-xs ${f.enabled ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>
                {f.enabled ? `${f.rollout}%` : "Off"}
              </span>
            </div>
            <p className="mt-0.5 text-xs text-gray-400">{f.description}</p>
          </div>
          <button onClick={() => onToggle(f.name, !f.enabled)}
            className={`relative h-6 w-11 rounded-full transition-colors ${f.enabled ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"}`}>
            <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${f.enabled ? "left-[1.375rem]" : "left-0.5"}`} />
          </button>
        </div>
      ))}
    </div>
  );
}
