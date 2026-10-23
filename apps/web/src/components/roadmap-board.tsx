"use client";

interface RoadmapItem { id: string; title: string; description: string;
  votes: number; quarter: string; tags: string[]; }
interface RoadmapBoardProps { columns: Record<string, RoadmapItem[]>;
  statuses: string[]; onVote: (id: string) => void; }

const STATUS_LABEL: Record<string, string> = {
  planned: "📋 Planned", in_progress: "🔄 In Progress",
  completed: "✅ Completed", shipped: "🚀 Shipped",
};

export function RoadmapBoard({ columns, statuses, onVote }: RoadmapBoardProps) {
  return (
    <div className="grid grid-cols-4 gap-4">
      {statuses.map(status => (
        <div key={status}>
          <h3 className="text-sm font-semibold mb-2">{STATUS_LABEL[status] || status}</h3>
          <div className="space-y-2">
            {(columns[status] || []).map(item => (
              <div key={item.id} className="rounded-lg border dark:border-gray-700 p-3">
                <p className="text-sm font-medium mb-1">{item.title}</p>
                {item.description && <p className="text-xs text-gray-500 mb-2">{item.description}</p>}
                <div className="flex items-center justify-between">
                  <button onClick={() => onVote(item.id)}
                    className="text-xs text-gray-400 hover:text-blue-600">▲ {item.votes}</button>
                  {item.quarter && <span className="text-xs text-gray-400">{item.quarter}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
