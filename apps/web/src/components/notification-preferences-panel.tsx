"use client";
import { useState } from "react";

interface NotifPrefs {
  channels: Record<string, boolean>;
  events: Record<string, boolean>;
  quietHoursStart: number;
  quietHoursEnd: number;
}

const channelLabels: Record<string, string> = { email: "📧 Email", in_app: "🔔 In-App", webhook: "🔗 Webhook", slack: "💬 Slack" };
const eventLabels: Record<string, string> = { install: "📥 Installs", uninstall: "📤 Uninstalls", review: "⭐ Reviews", update: "🔄 Updates", security: "🔒 Security", revenue: "💰 Revenue" };

export function NotificationPreferencesPanel({ prefs, onChange }: { prefs: NotifPrefs; onChange?: (prefs: NotifPrefs) => void }) {
  const [local, setLocal] = useState(prefs);
  const toggle = (type: "channels" | "events", key: string) => {
    const next = { ...local, [type]: { ...local[type], [key]: !local[type][key] } };
    setLocal(next);
    onChange?.(next);
  };
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold mb-2">Channels</h3>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(local.channels).map(([k, v]) => (
            <button key={k} onClick={() => toggle("channels", k)}
              className={`rounded-lg border p-2 text-xs text-left ${v ? "bg-blue-50 border-blue-300 dark:bg-blue-900/20 dark:border-blue-700" : "border-gray-200 dark:border-gray-700"}`}>
              {channelLabels[k] || k} {v ? "✓" : ""}
            </button>
          ))}
        </div>
      </div>
      <div>
        <h3 className="text-sm font-semibold mb-2">Events</h3>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(local.events).map(([k, v]) => (
            <button key={k} onClick={() => toggle("events", k)}
              className={`rounded-lg border p-2 text-xs text-left ${v ? "bg-green-50 border-green-300 dark:bg-green-900/20 dark:border-green-700" : "border-gray-200 dark:border-gray-700"}`}>
              {eventLabels[k] || k} {v ? "✓" : ""}
            </button>
          ))}
        </div>
      </div>
      <div className="text-xs text-gray-500">
        Quiet hours: {local.quietHoursStart}:00 — {local.quietHoursEnd}:00
        {local.quietHoursStart === local.quietHoursEnd && " (disabled)"}
      </div>
    </div>
  );
}
