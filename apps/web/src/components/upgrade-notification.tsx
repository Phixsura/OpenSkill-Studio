"use client";

interface UpgradeNotificationProps {
  appName: string; fromVersion: string; toVersion: string;
  breaking: boolean; changelog?: string; onUpgrade?: () => void; onDismiss?: () => void;
}

export function UpgradeNotification({ appName, fromVersion, toVersion, breaking, changelog, onUpgrade, onDismiss }: UpgradeNotificationProps) {
  return (
    <div className={`rounded-lg border p-4 ${breaking ? "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20" : "border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/20"}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="font-semibold">{breaking ? "⚠️" : "🆕"} {appName} v{toVersion} available</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">Currently on v{fromVersion}</p>
          {changelog && <p className="mt-1 text-sm">{changelog}</p>}
        </div>
        <div className="flex gap-2">
          {onDismiss && <button onClick={onDismiss} className="text-xs text-gray-500">Dismiss</button>}
          {onUpgrade && <button onClick={onUpgrade} className="rounded bg-blue-600 px-3 py-1 text-sm text-white">Upgrade</button>}
        </div>
      </div>
    </div>
  );
}
