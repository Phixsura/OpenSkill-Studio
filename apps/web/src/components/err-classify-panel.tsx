"use client";

interface ErrClassifyPanelProps { total: number; byClass: Record<string, number>;
  retryable: number; nonRetryable: number; }

const CLASS_COLORS: Record<string, string> = {
  transient: "bg-yellow-100 text-yellow-700", client: "bg-blue-100 text-blue-700",
  server: "bg-red-100 text-red-700", data: "bg-purple-100 text-purple-700",
  unknown: "bg-gray-200 text-gray-600",
};

export function ErrClassifyPanel({ total, byClass, retryable, nonRetryable }: ErrClassifyPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🏷️ Error Classification</h3>
        <span className="text-xs text-gray-400">{total} errors · {retryable} retryable</span>
      </div>
      <div className="flex gap-2 p-3 flex-wrap">
        {Object.entries(byClass).map(([cls, count]) => (
          <span key={cls} className={`px-2 py-1 text-xs rounded ${CLASS_COLORS[cls] ?? CLASS_COLORS.unknown}`}>
            {cls}: {count}
          </span>
        ))}
      </div>
    </div>
  );
}
