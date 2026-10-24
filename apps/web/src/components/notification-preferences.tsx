"use client";

interface Channel { label: string; icon: string; }
interface EventPref { id: string; label: string; category: string; channels: Record<string, boolean>; }
interface NotificationPreferencesProps { events: EventPref[]; channels: Channel[];
  categories: string[]; onToggle: (eventId: string, channel: string) => void; }

export function NotificationPreferences({ events, channels, categories, onToggle }: NotificationPreferencesProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Notification Preferences</h3>
      {categories.map(cat => (
        <div key={cat}>
          <p className="text-xs font-semibold text-gray-400 uppercase mb-2">{cat}</p>
          <div className="rounded-lg border dark:border-gray-700">
            <div className="flex items-center border-b px-4 py-2 dark:border-gray-700">
              <span className="flex-1 text-xs text-gray-400">Event</span>
              {channels.map(c => <span key={c.label} className="w-16 text-center text-xs text-gray-400">{c.icon}</span>)}
            </div>
            {events.filter(e => e.category === cat).map(e => (
              <div key={e.id} className="flex items-center px-4 py-2 border-b last:border-0 dark:border-gray-800">
                <span className="flex-1 text-sm">{e.label}</span>
                {channels.map(c => (
                  <div key={c.label} className="w-16 flex justify-center">
                    <input type="checkbox" checked={e.channels[c.label.toLowerCase()] ?? false}
                      onChange={() => onToggle(e.id, c.label.toLowerCase())} className="accent-blue-600" />
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
