"use client";

interface RoadmapItem { itemId: string; title: string; description: string; status: string; category: string; votes: number; eta: string; }

const statusCols: Record<string, string> = { planned: "Planned", in_progress: "In Progress", completed: "Done" };
const statusColors: Record<string, string> = {
  planned: "border-gray-300 dark:border-gray-600",
  in_progress: "border-blue-400", completed: "border-green-400",
};

export function PlatformRoadmapPanel({ items, onVote }: { items: RoadmapItem[]; onVote?: (id: string) => void }) {
  const columns = ["planned", "in_progress", "completed"];
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🗺️ Platform Roadmap</h2>
      <div className="grid grid-cols-3 gap-3">
        {columns.map((col) => (
          <div key={col}>
            <h3 className="text-sm font-bold mb-2 text-center">{statusCols[col]}</h3>
            <div className="space-y-1">
              {items.filter((i) => i.status === col).map((item) => (
                <div key={item.itemId} className={`rounded-lg border-l-4 ${statusColors[col]} border dark:border-gray-700 p-2`}>
                  <span className="font-semibold text-xs">{item.title}</span>
                  <p className="text-[10px] text-gray-500 mt-0.5">{item.description}</p>
                  <div className="flex justify-between mt-1">
                    <span className="text-[10px] text-gray-400">{item.category}</span>
                    <button onClick={() => onVote?.(item.itemId)} className="text-[10px] text-blue-600">▲ {item.votes}</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
