"use client";

interface NotifPref { eventType: string; email: boolean; inApp: boolean; push: boolean; webhook: boolean; }

export function NotifPreferencesPanel({ prefs, isDnd, onToggleDnd, onUpdate }: {
  prefs: NotifPref[]; isDnd: boolean;
  onToggleDnd?: () => void; onUpdate?: (event: string, channel: string, enabled: boolean) => void;
}) {
  const channels = ["email", "inApp", "push", "webhook"];
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🔔 Notification Preferences</h2>
        <button onClick={onToggleDnd}
          className={`text-xs px-3 py-1 rounded-full ${isDnd ? "bg-red-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          {isDnd ? "🔇 DND On" : "🔔 DND Off"}
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead><tr className="text-gray-500">
            <th className="text-left pb-2">Event</th>
            {channels.map((c) => <th key={c} className="text-center pb-2 capitalize">{c}</th>)}
          </tr></thead>
          <tbody>
            {prefs.map((p) => (
              <tr key={p.eventType} className="border-t dark:border-gray-700">
                <td className="py-1.5 font-mono">{p.eventType}</td>
                {channels.map((c) => (
                  <td key={c} className="text-center">
                    <input type="checkbox" checked={p[c as keyof NotifPref] as boolean}
                      onChange={(e) => onUpdate?.(p.eventType, c, e.target.checked)} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
