"use client";

interface NotificationItem { type: string; category?: string; summary?: string; count?: number; title?: string; message?: string; }
interface SmartNotificationCenterProps { items: NotificationItem[]; onDismiss: (index: number) => void; }

export function SmartNotificationCenter({ items, onDismiss }: SmartNotificationCenterProps) {
  if (items.length === 0) return <p className="text-sm text-gray-400">All caught up! 🎉</p>;
  return (
    <div className="space-y-2">
      {items.map((item, i) => (
        <div key={i} className="flex items-start justify-between rounded-lg border border-gray-200 p-3 dark:border-gray-700">
          <div>
            {item.type === "batch" ? (
              <p className="text-sm font-medium">📦 {item.summary}</p>
            ) : (
              <>
                <p className="text-sm font-medium">{item.title || item.category}</p>
                {item.message && <p className="text-xs text-gray-500">{item.message}</p>}
              </>
            )}
          </div>
          <button onClick={() => onDismiss(i)} className="text-xs text-gray-400 hover:text-gray-600">✕</button>
        </div>
      ))}
    </div>
  );
}
