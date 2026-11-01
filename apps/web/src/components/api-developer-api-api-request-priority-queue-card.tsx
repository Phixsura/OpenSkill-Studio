"use client";

interface Props { queueSize: number; distribution: Record<string, number>; appName: string; }

const pColor: Record<string, string> = { critical: "text-red-600", high: "text-orange-600", normal: "text-blue-600", low: "text-gray-500" };

export default function APIDeveloperAPIApiRequestPriorityQueueCard({ queueSize, distribution, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">⏫ Priority Queue</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-sm font-bold text-blue-600">{queueSize}</span>
      </div>
      <div className="grid grid-cols-4 gap-2 text-center">
        {["critical", "high", "normal", "low"].map((p) => (
          <div key={p} className="rounded bg-gray-50 py-1.5 dark:bg-gray-800">
            <p className={`text-sm font-bold ${pColor[p]}`}>{distribution[p] ?? 0}</p>
            <p className="text-[8px] text-gray-400">{p}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
