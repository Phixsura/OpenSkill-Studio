"use client";

interface AdminLog { actionId: string; adminId: string; action: string; targetType: string; targetId: string; reason: string; timestamp: number; }

const actionIcons: Record<string, string> = {
  suspend_extension: "⛔", unsuspend_extension: "✅", ban_developer: "🚫",
  unban_developer: "🔓", remove_review: "🗑️", feature_extension: "⭐",
  unfeature_extension: "☆", approve_extension: "✅", reject_extension: "❌",
};

export function AdminConsolePanel({ logs, onAction }: {
  logs: AdminLog[]; onAction?: (action: string, targetId: string, reason: string) => void;
}) {
  return (
    <div className="space-y-3">
      <h3 className="font-bold text-sm">Admin Console</h3>
      <div className="space-y-1">
        {logs.map(l => (
          <div key={l.actionId} className="flex items-start gap-2 border dark:border-gray-700 rounded-lg p-2 text-xs">
            <span>{actionIcons[l.action] || "📌"}</span>
            <div className="flex-1">
              <span className="font-medium">{l.adminId}</span>
              <span className="text-gray-500"> → {l.action.replace(/_/g, " ")}</span>
              <span className="text-blue-500 ml-1">{l.targetId}</span>
              {l.reason && <p className="text-gray-400 mt-0.5">"{l.reason}"</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
