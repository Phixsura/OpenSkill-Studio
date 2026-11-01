"use client";

interface NotificationComposerProps { title: string; body: string; icon: string;
  priority: string; channels: string[]; actionUrl: string; }

const PRI_STYLE: Record<string, string> = {
  critical: "bg-red-100 text-red-700", high: "bg-orange-100 text-orange-700",
  normal: "bg-blue-100 text-blue-700",
};
const CH_ICON: Record<string, string> = {
  in_app: "🔔", email: "📧", slack: "💬", sms: "📱",
};

export function NotificationComposer({ title, body, icon, priority, channels, actionUrl }: NotificationComposerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-4">
      <div className="flex items-start gap-3 mb-3">
        <span className="text-2xl">{icon}</span>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-bold">{title}</h4>
            <span className={`text-xs px-1.5 py-0.5 rounded ${PRI_STYLE[priority] || ""}`}>{priority}</span>
          </div>
          <p className="text-sm text-gray-500 mt-0.5">{body}</p>
        </div>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex gap-1">
          {channels.map(ch => (
            <span key={ch} className="text-xs px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded">{CH_ICON[ch] || "📌"} {ch}</span>
          ))}
        </div>
        {actionUrl && <span className="text-xs text-blue-600">View →</span>}
      </div>
    </div>
  );
}
