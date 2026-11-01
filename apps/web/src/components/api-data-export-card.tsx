"use client";

interface ExportInfo {
  export_id: string;
  format: string;
  resource: string;
  status: "pending" | "processing" | "completed" | "failed";
  record_count: number;
  file_size_bytes: number;
}

interface APIDataExportCardProps {
  exports: ExportInfo[];
  appName: string;
}

const statusStyle: Record<string, string> = {
  pending: "bg-gray-100 text-gray-500 dark:bg-gray-800",
  processing: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  completed: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

function formatBytes(b: number): string {
  if (b < 1024) return `${b}B`;
  if (b < 1048576) return `${(b / 1024).toFixed(1)}KB`;
  return `${(b / 1048576).toFixed(1)}MB`;
}

export default function APIDataExportCard({ exports: exps, appName }: APIDataExportCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📥 Data Exports</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{exps.length} exports</span>
      </div>

      {exps.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No data exports</p>
      ) : (
        <div className="space-y-1.5">
          {exps.map((e) => (
            <div key={e.export_id} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusStyle[e.status]}`}>{e.status}</span>
                <span className="text-xs text-gray-700 dark:text-gray-300">{e.resource}</span>
                <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{e.format}</span>
              </div>
              {e.status === "completed" && <span className="text-[10px] text-gray-400">{e.record_count} rows · {formatBytes(e.file_size_bytes)}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
