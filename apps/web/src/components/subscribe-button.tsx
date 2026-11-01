"use client";

interface SubscribeButtonProps { subscribed: boolean; subscriberCount: number; onToggle: () => void; }

export function SubscribeButton({ subscribed, subscriberCount, onToggle }: SubscribeButtonProps) {
  return (
    <button onClick={onToggle} className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm transition ${
      subscribed ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200" : "border border-gray-300 text-gray-600 hover:bg-gray-100"
    }`}>
      {subscribed ? "🔔 Subscribed" : "🔕 Subscribe"}
      <span className="text-xs opacity-70">{subscriberCount}</span>
    </button>
  );
}
