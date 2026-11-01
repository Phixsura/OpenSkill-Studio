"use client";

interface ModItem { itemId: string; contentType: string; content: string; authorId: string; status: string; extensionId: string; }

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700", escalated: "bg-red-100 text-red-700",
  approved: "bg-green-100 text-green-700", rejected: "bg-gray-100 text-gray-700",
};

export function ModerationQueuePanel({ items, onAction }: {
  items: ModItem[]; onAction?: (itemId: string, action: "approved" | "rejected") => void;
}) {
  if (!items.length) return <div className="text-center text-green-600 py-6 text-sm">✅ Queue empty — all caught up!</div>;
  return (
    <div className="space-y-2">
      <div className="text-xs text-gray-500 font-medium">{items.length} items pending review</div>
      {items.map(item => (
        <div key={item.itemId} className="border dark:border-gray-700 rounded-xl p-3 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className={`text-xs px-2 py-0.5 rounded-full ${statusColors[item.status] || ""}`}>{item.status}</span>
              <span className="text-xs text-gray-500">{item.contentType} · {item.extensionId}</span>
            </div>
            <span className="text-xs text-gray-400">by {item.authorId}</span>
          </div>
          <p className="text-sm bg-gray-50 dark:bg-gray-800 rounded-lg p-2">{item.content}</p>
          <div className="flex gap-2">
            <button onClick={() => onAction?.(item.itemId, "approved")} className="text-xs bg-green-500 text-white px-3 py-1 rounded-lg">✓ Approve</button>
            <button onClick={() => onAction?.(item.itemId, "rejected")} className="text-xs bg-red-500 text-white px-3 py-1 rounded-lg">✕ Reject</button>
          </div>
        </div>
      ))}
    </div>
  );
}
