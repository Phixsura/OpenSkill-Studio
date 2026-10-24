"use client";

interface Flag { id: string; description: string; enabled: boolean; rollout_pct: number; }
interface FeatureFlagPanelV2Props { flags: Flag[]; }

export function FeatureFlagPanelV2({ flags }: FeatureFlagPanelV2Props) {
  const enabled = flags.filter(f => f.enabled).length;
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">Feature Flags</h3>
        <span className="text-xs text-gray-400">{enabled}/{flags.length} enabled</span>
      </div>
      <ul className="mt-3 space-y-2">
        {flags.map(f => (
          <li key={f.id} className="flex items-center justify-between text-sm">
            <div>
              <span className="font-medium">{f.id}</span>
              <p className="text-xs text-gray-400">{f.description}</p>
            </div>
            <div className="flex items-center gap-2">
              {f.rollout_pct < 100 && f.enabled && (
                <span className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700">{f.rollout_pct}%</span>
              )}
              <span className={`h-2.5 w-2.5 rounded-full ${f.enabled ? "bg-green-500" : "bg-gray-300"}`} />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
