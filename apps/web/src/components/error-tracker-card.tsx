"use client";

interface ErrorGroupInfo {
  fingerprint: string;
  message: string;
  source: string;
  count: number;
  resolved: boolean;
}

interface ErrorTrackerCardProps {
  errors: ErrorGroupInfo[];
  unresolvedCount: number;
  appName: string;
}

export default function ErrorTrackerCard({ errors, unresolvedCount, appName }: ErrorTrackerCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🐛 Error Tracker</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{errors.length} groups</span>
          {unresolvedCount > 0 && <p className="text-[10px] text-red-500">{unresolvedCount} unresolved</p>}
        </div>
      </div>

      {errors.length === 0 ? (
        <p className="text-center text-sm text-green-600 dark:text-green-400">No errors tracked</p>
      ) : (
        <div className="space-y-1.5">
          {errors.map((e) => (
            <div key={e.fingerprint} className={`rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800 ${e.resolved ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-700 dark:text-gray-300 truncate max-w-[200px]">{e.message}</span>
                <span className="text-sm font-bold text-gray-900 dark:text-gray-100">{e.count}x</span>
              </div>
              <p className="text-[10px] text-gray-400">{e.source}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
