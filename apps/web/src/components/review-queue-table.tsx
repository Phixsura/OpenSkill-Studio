"use client";

interface ReviewItem { appId: string; appName: string; version: string; submittedBy: string; submittedAt: string; status: string; reviewerId?: string; }

interface ReviewQueueTableProps { items: ReviewItem[]; onAssign?: (appId: string) => void; onReview?: (appId: string) => void; }

const STATUS_BADGES: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800", in_review: "bg-blue-100 text-blue-800",
  approved: "bg-green-100 text-green-800", rejected: "bg-red-100 text-red-800",
};

export function ReviewQueueTable({ items, onAssign, onReview }: ReviewQueueTableProps) {
  if (items.length === 0) return <p className="py-4 text-center text-sm text-gray-400">No reviews in queue</p>;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead><tr className="border-b dark:border-gray-700">
          <th className="px-3 py-2">App</th><th className="px-3 py-2">Version</th>
          <th className="px-3 py-2">Status</th><th className="px-3 py-2">Submitted</th>
          <th className="px-3 py-2">Actions</th>
        </tr></thead>
        <tbody>
          {items.map(item => (
            <tr key={item.appId} className="border-b dark:border-gray-800">
              <td className="px-3 py-2 font-medium">{item.appName}</td>
              <td className="px-3 py-2 font-mono text-xs">{item.version}</td>
              <td className="px-3 py-2"><span className={`rounded-full px-2 py-0.5 text-xs ${STATUS_BADGES[item.status] ?? "bg-gray-100"}`}>{item.status}</span></td>
              <td className="px-3 py-2 text-xs text-gray-500">{item.submittedAt}</td>
              <td className="px-3 py-2">
                {item.status === "pending" && onAssign && <button onClick={() => onAssign(item.appId)} className="text-xs text-blue-600">Assign</button>}
                {item.status === "in_review" && onReview && <button onClick={() => onReview(item.appId)} className="text-xs text-green-600">Review</button>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
