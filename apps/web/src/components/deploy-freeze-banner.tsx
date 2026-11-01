"use client";

interface DeployFreezeBannerProps { frozen: boolean; reason: string | null;
  freezeCount: number; onCancel: () => void; }

export function DeployFreezeBanner({ frozen, reason, freezeCount, onCancel }: DeployFreezeBannerProps) {
  if (!frozen) {
    return (
      <div className="rounded-xl border border-green-300 dark:border-green-800 p-4 bg-green-50 dark:bg-green-900/10">
        <div className="flex items-center gap-2">
          <span className="text-green-600 text-lg">✅</span>
          <span className="text-sm font-medium text-green-700 dark:text-green-400">Deployments Active</span>
        </div>
      </div>
    );
  }
  return (
    <div className="rounded-xl border border-red-300 dark:border-red-800 p-4 bg-red-50 dark:bg-red-900/10">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-red-600 text-lg">🚫</span>
          <div>
            <div className="text-sm font-medium text-red-700 dark:text-red-400">Deploy Freeze Active</div>
            <div className="text-xs text-red-500">{reason} · {freezeCount} freeze(s)</div>
          </div>
        </div>
        <button onClick={onCancel} className="px-3 py-1 text-xs bg-red-500 text-white rounded-lg">Cancel Freeze</button>
      </div>
    </div>
  );
}
