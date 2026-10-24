"use client";

interface FlagResult { flag: string; value: boolean; reason: string; }
interface FeatureFlagPanelProps { flags: FlagResult[]; userId: string; enabledCount: number; }

export function FeatureFlagPanel({ flags, userId, enabledCount }: FeatureFlagPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🚩 Feature Flags</h3>
        <span className="text-xs text-gray-400">user: {userId} · {enabledCount}/{flags.length} on</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {flags.map(f => (
          <div key={f.flag} className="flex items-center justify-between px-4 py-2 text-xs">
            <span className="font-mono">{f.flag}</span>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">{f.reason}</span>
              <span className={`w-2 h-2 rounded-full ${f.value ? "bg-green-500" : "bg-gray-400"}`} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
