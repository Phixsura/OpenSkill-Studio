"use client";

interface AlertPref { metric: string; threshold: number; unit: string; channel: string; enabled: boolean; }
interface AlertSettingsFormProps { alerts: AlertPref[];
  onToggle: (metric: string) => void; onSave: () => void; }

const CHANNEL_ICON: Record<string, string> = { email: "📧", slack: "💬", pagerduty: "📟" };

export function AlertSettingsForm({ alerts, onToggle, onSave }: AlertSettingsFormProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🔔 Alert Settings</h3>
        <button onClick={onSave} className="text-xs px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700">Save</button>
      </div>
      <div className="space-y-2">
        {alerts.map(a => (
          <div key={a.metric} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-2.5">
            <div className="flex items-center gap-2">
              <button onClick={() => onToggle(a.metric)}
                className={`w-8 h-4 rounded-full ${a.enabled ? "bg-green-500" : "bg-gray-300"}`}>
                <span className={`block w-3 h-3 rounded-full bg-white transform ${a.enabled ? "translate-x-4" : "translate-x-0.5"}`} />
              </button>
              <span className="text-sm capitalize">{a.metric.replace("_", " ")}</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <span>{a.threshold}{a.unit}</span>
              <span>{CHANNEL_ICON[a.channel] || "📌"} {a.channel}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
