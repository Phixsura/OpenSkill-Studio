"use client";

import { useState } from "react";

interface NotificationCategory {
  id: string;
  label: string;
  description: string;
  icon: string;
}

interface ChannelPreference {
  categoryId: string;
  email: boolean;
  inApp: boolean;
  slack: boolean;
}

const categories: NotificationCategory[] = [
  { id: "installs", label: "New Installs", description: "When someone installs your extension", icon: "⬇️" },
  { id: "reviews", label: "Reviews", description: "New reviews and ratings", icon: "⭐" },
  { id: "security", label: "Security Alerts", description: "Security scan results and vulnerabilities", icon: "🔒" },
  { id: "billing", label: "Billing", description: "Subscription and payment updates", icon: "💰" },
  { id: "updates", label: "Platform Updates", description: "API changes and deprecations", icon: "📢" },
  { id: "support", label: "Support Tickets", description: "New tickets and replies", icon: "🎫" },
];

export function NotificationPreferencesPanel({
  preferences,
  onSave,
}: {
  preferences: ChannelPreference[];
  onSave?: (prefs: ChannelPreference[]) => void;
}) {
  const [prefs, setPrefs] = useState<ChannelPreference[]>(preferences);
  const [saved, setSaved] = useState(false);

  const toggle = (categoryId: string, channel: "email" | "inApp" | "slack") => {
    setPrefs((prev) =>
      prev.map((p) => p.categoryId === categoryId ? { ...p, [channel]: !p[channel] } : p)
    );
    setSaved(false);
  };

  const handleSave = () => {
    onSave?.(prefs);
    setSaved(true);
  };

  const getPref = (catId: string) => prefs.find((p) => p.categoryId === catId) || { categoryId: catId, email: true, inApp: true, slack: false };

  return (
    <div className="space-y-5">
      <h2 className="text-lg font-bold">🔔 Notification Preferences</h2>

      <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-gray-50 dark:bg-gray-800 text-left text-xs text-gray-500">
              <th className="px-4 py-2">Category</th>
              <th className="px-4 py-2 text-center">📧 Email</th>
              <th className="px-4 py-2 text-center">🔔 In-App</th>
              <th className="px-4 py-2 text-center">💬 Slack</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((cat) => {
              const p = getPref(cat.id);
              return (
                <tr key={cat.id} className="border-t dark:border-gray-700">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span>{cat.icon}</span>
                      <div>
                        <div className="font-medium">{cat.label}</div>
                        <div className="text-xs text-gray-400">{cat.description}</div>
                      </div>
                    </div>
                  </td>
                  {(["email", "inApp", "slack"] as const).map((ch) => (
                    <td key={ch} className="px-4 py-3 text-center">
                      <button
                        onClick={() => toggle(cat.id, ch)}
                        className={`w-8 h-5 rounded-full transition ${p[ch] ? "bg-blue-500" : "bg-gray-300 dark:bg-gray-600"}`}
                      >
                        <div className={`w-4 h-4 rounded-full bg-white transition transform ${p[ch] ? "translate-x-3.5" : "translate-x-0.5"}`} />
                      </button>
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="flex items-center gap-3">
        <button onClick={handleSave} className="rounded-lg bg-blue-600 text-white px-4 py-2 text-sm font-medium">
          Save Preferences
        </button>
        {saved && <span className="text-sm text-green-500">✅ Saved!</span>}
      </div>
    </div>
  );
}
