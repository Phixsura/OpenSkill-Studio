"use client";

interface ChangelogSubscribeToggleProps { appName: string; subscribed: boolean;
  subscriberCount: number; onToggle: () => void; }

export function ChangelogSubscribeToggle({ appName, subscribed, subscriberCount, onToggle }: ChangelogSubscribeToggleProps) {
  return (
    <div className="flex items-center gap-3">
      <button onClick={onToggle}
        className={`inline-flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg transition ${
          subscribed ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-600 hover:bg-blue-50"
        }`}>
        <span>{subscribed ? "🔔" : "🔕"}</span>
        {subscribed ? "Subscribed" : "Subscribe to updates"}
      </button>
      <span className="text-xs text-gray-400">{subscriberCount.toLocaleString()} subscribers</span>
    </div>
  );
}
