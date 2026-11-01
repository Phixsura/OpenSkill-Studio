"use client";

interface NotifCategory { id: string; label: string; icon: string;
  channels: Record<string, boolean>; editable: boolean; }
interface NotificationPrefsPageProps { categories: NotifCategory[];
  channels: string[]; onToggle: (catId: string, channel: string) => void; }

export function NotificationPrefsPage({ categories, channels, onToggle }: NotificationPrefsPageProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔔 Notification Preferences</h3>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3 text-left">Category</th>
          {channels.map(ch => <th key={ch} className="p-3 text-center capitalize">{ch.replace("_", " ")}</th>)}
        </tr></thead>
        <tbody>
          {categories.map(cat => (
            <tr key={cat.id} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3">{cat.icon} {cat.label}
                {!cat.editable && <span className="text-xs text-gray-400 ml-1">(required)</span>}
              </td>
              {channels.map(ch => (
                <td key={ch} className="p-3 text-center">
                  <button onClick={() => cat.editable && onToggle(cat.id, ch)} disabled={!cat.editable}
                    className={`w-8 h-4 rounded-full ${cat.channels[ch] ? "bg-blue-500" : "bg-gray-300"} ${!cat.editable ? "opacity-50" : ""}`}>
                    <span className={`block w-3 h-3 rounded-full bg-white transform ${cat.channels[ch] ? "translate-x-4" : "translate-x-0.5"}`} />
                  </button>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
