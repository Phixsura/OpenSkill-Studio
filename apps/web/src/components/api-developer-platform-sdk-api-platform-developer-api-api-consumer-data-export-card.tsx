"use client";

interface ExportInfo { job_id: string; consumer_id: string; format: string; status: string; data_types: string[]; record_count: number; file_size_kb: number; }
interface Props { exports: ExportInfo[]; appName: string; }

const statusIcon: Record<string, string> = { pending: "⏳", processing: "⚙️", completed: "✅", failed: "❌" };

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDataExportCard({ exports: exps, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📤 Data Exports</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {exps.length} exports</p>
      </div>
      {exps.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No exports</p>
      ) : (
        <div className="space-y-1.5">
          {exps.map((e) => (
            <div key={e.job_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{statusIcon[e.status] ?? "•"} {e.consumer_id}</span>
                <span className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">{e.format.toUpperCase()}</span>
              </div>
              {e.status === "completed" && <div className="text-[10px] text-gray-400">{e.record_count.toLocaleString()} records · {e.file_size_kb} KB</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
