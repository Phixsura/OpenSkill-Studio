"use client";

interface ModerationItem { id: string; status: string; flags: string[]; safeText: string; }
interface ModerationQueueTableProps { items: ModerationItem[]; counts: Record<string, number>; queueHealth: string; }

const STATUS_BADGE: Record<string, string> = {
  approved: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  flagged: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  rejected: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export function ModerationQueueTable({ items, counts, queueHealth }: ModerationQueueTableProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🛡️ Moderation Queue</h3>
        <span className={`text-xs px-2 py-1 rounded-full ${queueHealth === "clean" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
          {queueHealth === "clean" ? "✅ Clean" : "⚠️ Needs Review"}
        </span>
      </div>
      <div className="flex gap-4 px-4 py-2 text-xs text-gray-500 border-b dark:border-gray-700">
        <span>Approved: {counts.approved}</span>
        <span>Flagged: {counts.flagged}</span>
        <span>Rejected: {counts.rejected}</span>
      </div>
      <table className="w-full text-sm">
        <thead><tr className="text-left text-xs text-gray-400 border-b dark:border-gray-700">
          <th className="p-3">ID</th><th className="p-3">Content</th>
          <th className="p-3">Status</th><th className="p-3">Flags</th>
        </tr></thead>
        <tbody>
          {items.map(item => (
            <tr key={item.id} className="border-b last:border-0 dark:border-gray-700">
              <td className="p-3 font-mono text-xs">{item.id}</td>
              <td className="p-3 max-w-xs truncate">{item.safeText}</td>
              <td className="p-3">
                <span className={`text-xs px-2 py-0.5 rounded-full ${STATUS_BADGE[item.status] || ""}`}>
                  {item.status}
                </span>
              </td>
              <td className="p-3 text-xs text-gray-400">{item.flags.join(", ") || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
