"use client";

interface UpdateNotif { notifId: string; extensionId: string; oldVersion: string; newVersion: string; changelog: string[]; breaking: boolean; }

export function UpdateNotificationFeed({ notifications, onUpdate }: {
  notifications: UpdateNotif[]; onUpdate?: (extId: string, version: string) => void;
}) {
  if (!notifications.length) return <div className="text-center text-gray-400 py-6 text-sm">All extensions up to date ✨</div>;
  return (
    <div className="space-y-2">
      {notifications.map(n => (
        <div key={n.notifId} className={`border rounded-xl p-3 ${n.breaking ? "border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-900/10" : "border-gray-200 dark:border-gray-700"}`}>
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              {n.breaking && <span className="text-xs bg-red-500 text-white px-1.5 py-0.5 rounded">BREAKING</span>}
              <span className="font-medium text-sm">{n.extensionId}</span>
              <span className="text-xs text-gray-500">{n.oldVersion} → {n.newVersion}</span>
            </div>
            <button onClick={() => onUpdate?.(n.extensionId, n.newVersion)}
              className="text-xs bg-blue-500 text-white px-2 py-1 rounded-lg">Update</button>
          </div>
          <ul className="text-xs text-gray-500 ml-4">
            {n.changelog.map((c, i) => <li key={i}>• {c}</li>)}
          </ul>
        </div>
      ))}
    </div>
  );
}
