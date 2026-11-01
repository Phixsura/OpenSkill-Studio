"use client";

interface NotificationPrefsPanelProps {
  prefs: Record<string, Record<string, boolean>>;
  channels: string[];
  categories: string[];
  onToggle: (category: string, channel: string, enabled: boolean) => void;
}

const CAT_ICON: Record<string, string> = {
  security: "🔒", billing: "💳", deploy: "🚀",
  review: "👀", mention: "💬", marketing: "📢",
};

export function NotificationPrefsPanel({ prefs, channels, categories, onToggle }: NotificationPrefsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔔 Notification Preferences</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="text-xs text-gray-400 border-b dark:border-gray-700">
            <th className="p-3 text-left">Category</th>
            {channels.map(ch => <th key={ch} className="p-3 text-center capitalize">{ch.replace("_", " ")}</th>)}
          </tr></thead>
          <tbody>
            {categories.map(cat => (
              <tr key={cat} className="border-b last:border-0 dark:border-gray-700">
                <td className="p-3 capitalize">{CAT_ICON[cat] || "📌"} {cat}</td>
                {channels.map(ch => (
                  <td key={ch} className="p-3 text-center">
                    <button onClick={() => onToggle(cat, ch, !prefs[cat]?.[ch])}
                      className={`w-8 h-5 rounded-full transition ${prefs[cat]?.[ch] ? "bg-blue-500" : "bg-gray-300 dark:bg-gray-600"}`}>
                      <span className={`block w-3.5 h-3.5 rounded-full bg-white transition transform ${prefs[cat]?.[ch] ? "translate-x-3.5" : "translate-x-0.5"}`} />
                    </button>
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
