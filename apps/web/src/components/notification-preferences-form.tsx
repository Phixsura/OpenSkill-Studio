"use client";

interface EventPref { channels: string[]; enabled: boolean; }
interface NotificationPreferencesFormProps {
  preferences: Record<string, EventPref>;
  eventLabels: Record<string, string>;
  channels: string[];
  onUpdate: (eventType: string, channels: string[], enabled: boolean) => void;
}

export function NotificationPreferencesForm({ preferences, eventLabels, channels, onUpdate }: NotificationPreferencesFormProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Notification Preferences</h3>
      <div className="mt-3 overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b dark:border-gray-700">
              <th className="py-2 text-left text-xs">Event</th>
              <th className="py-2 text-center text-xs">Enabled</th>
              {channels.map(ch => <th key={ch} className="py-2 text-center text-xs capitalize">{ch.replace("_", " ")}</th>)}
            </tr>
          </thead>
          <tbody>
            {Object.entries(preferences).map(([et, pref]) => (
              <tr key={et} className="border-b dark:border-gray-700">
                <td className="py-2 text-xs">{eventLabels[et] || et}</td>
                <td className="py-2 text-center">
                  <input type="checkbox" checked={pref.enabled} onChange={e => onUpdate(et, pref.channels, e.target.checked)} />
                </td>
                {channels.map(ch => (
                  <td key={ch} className="py-2 text-center">
                    <input type="checkbox" checked={pref.channels.includes(ch)} disabled={!pref.enabled}
                      onChange={e => {
                        const newCh = e.target.checked ? [...pref.channels, ch] : pref.channels.filter(c => c !== ch);
                        onUpdate(et, newCh, pref.enabled);
                      }} />
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
