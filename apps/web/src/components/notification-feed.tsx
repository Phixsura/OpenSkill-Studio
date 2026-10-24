"use client";

interface Notification { recipient: string; channel: string; title: string;
  body: string; priority: string; status: string; }
interface NotificationFeedProps { notifications: Notification[]; total: number; }

const CH_ICONS: Record<string, string> = {
  email: "📧", push: "📱", slack: "💬", in_app: "🔔", sms: "📲",
};

export function NotificationFeed({ notifications, total }: NotificationFeedProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔔 Notifications</h3>
        <span className="text-xs text-gray-400">{total} sent</span>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-64 overflow-y-auto">
        {notifications.map((n, i) => (
          <div key={i} className="px-4 py-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span>{CH_ICONS[n.channel] ?? "📨"}</span>
                <span className="text-sm font-medium">{n.title}</span>
              </div>
              <span className={`text-[10px] px-1.5 py-0.5 rounded ${n.priority === "high" ? "bg-red-100 text-red-600" : "bg-gray-100 text-gray-500 dark:bg-gray-800"}`}>{n.priority}</span>
            </div>
            <div className="text-xs text-gray-400 mt-0.5 truncate">{n.body}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
