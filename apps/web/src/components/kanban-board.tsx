"use client";

interface KanbanCard { id: string; title: string; assignee: string; priority: string; labels: string[]; }
interface KanbanColumn { id: string; title: string; cards: KanbanCard[]; card_count: number; wip_limit: number | null; over_limit: boolean; }
interface KanbanBoardProps { columns: KanbanColumn[]; }

const priorityColors: Record<string, string> = {
  high: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  low: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
};

export function KanbanBoard({ columns }: KanbanBoardProps) {
  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {columns.map(col => (
        <div key={col.id} className="flex w-72 flex-shrink-0 flex-col rounded-lg border bg-gray-50 dark:bg-gray-900 dark:border-gray-700">
          <div className={`flex items-center justify-between border-b px-3 py-2 ${col.over_limit ? "bg-red-50 dark:bg-red-900/20" : ""}`}>
            <h3 className="text-sm font-semibold">{col.title}</h3>
            <span className="text-xs text-gray-400">
              {col.card_count}{col.wip_limit != null && `/${col.wip_limit}`}
            </span>
          </div>
          <div className="flex-1 space-y-2 p-2">
            {col.cards.map(card => (
              <div key={card.id} className="rounded-md border bg-white p-3 shadow-sm dark:bg-gray-800 dark:border-gray-700">
                <p className="text-sm font-medium">{card.title}</p>
                <div className="mt-2 flex items-center justify-between">
                  <span className={`rounded px-1.5 py-0.5 text-xs ${priorityColors[card.priority] ?? ""}`}>{card.priority}</span>
                  {card.assignee && <span className="text-xs text-gray-400">{card.assignee}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
