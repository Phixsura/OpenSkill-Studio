"use client";

interface StatusAggregatorProps { overallScore: number; status: string;
  scores: Record<string, number>; }

const STATUS_STYLES: Record<string, { bg: string; label: string; color: string }> = {
  operational: { bg: "bg-green-50 dark:bg-green-900/10", label: "All Systems Operational", color: "text-green-600" },
  degraded: { bg: "bg-yellow-50 dark:bg-yellow-900/10", label: "Degraded Performance", color: "text-yellow-600" },
  outage: { bg: "bg-red-50 dark:bg-red-900/10", label: "System Outage", color: "text-red-600" },
};

export function StatusAggregator({ overallScore, status, scores }: StatusAggregatorProps) {
  const s = STATUS_STYLES[status] ?? STATUS_STYLES.operational;
  return (
    <div className={`rounded-xl border dark:border-gray-700 overflow-hidden ${s.bg}`}>
      <div className="p-6 text-center">
        <div className={`text-4xl font-bold ${s.color}`}>{overallScore}</div>
        <div className={`text-sm mt-1 font-medium ${s.color}`}>{s.label}</div>
      </div>
      <div className="grid grid-cols-5 gap-px bg-gray-200 dark:bg-gray-700">
        {Object.entries(scores).map(([key, val]) => (
          <div key={key} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className="text-sm font-bold">{val}</div>
            <div className="text-[9px] text-gray-400 capitalize">{key}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
