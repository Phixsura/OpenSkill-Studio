"use client";

interface Export { id: string; format: string; status: string; recordCount: number; sizeBytes: number; createdAt: string; }
interface Props { exports: Export[]; consumerId: string; appName: string; }

const statusColors: Record<string, string> = {
  pending: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400",
  processing: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  completed: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  failed: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerDataExportCard({ exports, consumerId, appName }: Props) {
  const fmtSize = (b: number) => b > 1024 ? `${(b / 1024).toFixed(1)} KB` : `${b} B`;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📦 Data Exports</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {consumerId}</p>
      </div>
      {exports.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No exports</p>
      ) : (
        <div className="space-y-2">
          {exports.map((e) => (
            <div key={e.id} className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-800">
              <div>
                <div className="text-[11px] font-medium text-gray-700 dark:text-gray-300">{e.format.toUpperCase()} · {e.recordCount} records</div>
                <div className="text-[10px] text-gray-400">{fmtSize(e.sizeBytes)} · {e.createdAt}</div>
              </div>
              <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusColors[e.status] ?? ""}`}>{e.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
