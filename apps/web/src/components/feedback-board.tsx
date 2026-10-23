"use client";

interface FeedbackItem { feedback_id: string; title: string; category: string;
  status: string; votes: number; }
interface FeedbackBoardProps { columns: Record<string, FeedbackItem[]>; total: number;
  onVote: (id: string) => void; onStatusChange: (id: string, status: string) => void; }

const statusLabels: Record<string, { label: string; color: string }> = {
  open: { label: "Open", color: "bg-blue-100 dark:bg-blue-900/30" },
  planned: { label: "Planned", color: "bg-purple-100 dark:bg-purple-900/30" },
  in_progress: { label: "In Progress", color: "bg-yellow-100 dark:bg-yellow-900/30" },
  shipped: { label: "Shipped", color: "bg-green-100 dark:bg-green-900/30" },
  declined: { label: "Declined", color: "bg-gray-100 dark:bg-gray-800" },
};
const catIcon: Record<string, string> = { bug: "🐛", feature: "💡", improvement: "✨", question: "❓" };

export function FeedbackBoard({ columns, total, onVote }: FeedbackBoardProps) {
  const visibleStatuses = ["open", "planned", "in_progress", "shipped"];
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Feedback Board</h2>
        <span className="text-xs text-gray-400">{total} items</span>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {visibleStatuses.map(status => {
          const s = statusLabels[status] ?? statusLabels.open;
          const items = columns[status] ?? [];
          return (
            <div key={status} className={`rounded-lg p-3 ${s.color}`}>
              <h3 className="text-xs font-semibold uppercase">{s.label} ({items.length})</h3>
              <div className="mt-2 space-y-1.5">
                {items.slice(0, 5).map(item => (
                  <div key={item.feedback_id} className="rounded bg-white p-2 shadow-sm dark:bg-gray-900">
                    <div className="flex items-start gap-1.5">
                      <button onClick={() => onVote(item.feedback_id)}
                        className="flex flex-col items-center text-xs text-gray-400 hover:text-blue-500">
                        <span>▲</span><span>{item.votes}</span>
                      </button>
                      <div>
                        <p className="text-xs font-medium">{item.title}</p>
                        <span className="text-[10px]">{catIcon[item.category] ?? ""}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
