"use client";

interface RoadmapInfo { item_id: string; title: string; target_version: string; status: string; vote_count: number; }
interface Props { items: RoadmapInfo[]; appName: string; }

const statusStyle: Record<string, string> = {
  planned: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  in_progress: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  completed: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  cancelled: "bg-gray-100 text-gray-500 dark:bg-gray-800",
};

export default function APIChangelogRoadmapCard({ items, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🗺️ Roadmap</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{items.length} items</span>
      </div>
      {items.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No roadmap items</p>
      ) : (
        <div className="space-y-1.5">
          {items.map((i) => (
            <div key={i.item_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusStyle[i.status] ?? ""}`}>{i.status.replace("_", " ")}</span>
                <span className="text-gray-700 dark:text-gray-300">{i.title}</span>
              </div>
              <div className="flex items-center gap-1.5 text-gray-400">
                <span>{i.target_version}</span>
                <span>👍 {i.vote_count}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
