"use client";

interface ExportInfo {
  export_id: string;
  resource_type: string;
  format: "json" | "csv" | "parquet";
  status: "pending" | "processing" | "completed" | "failed" | "expired";
  created_at: string;
  file_size_bytes: number;
  row_count: number;
  error_message: string | null;
}

interface DataExportCardProps {
  exports: ExportInfo[];
  appName: string;
}

const STATUS_STYLES: Record<string, { icon: string; text: string }> = {
  pending: { icon: "⏳", text: "text-gray-500" },
  processing: { icon: "⚙️", text: "text-blue-600 dark:text-blue-400" },
  completed: { icon: "✅", text: "text-green-600 dark:text-green-400" },
  failed: { icon: "❌", text: "text-red-600 dark:text-red-400" },
  expired: { icon: "🕐", text: "text-gray-400" },
};

const FORMAT_BADGES: Record<string, string> = {
  json: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  csv: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  parquet: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
};

function formatBytes(bytes: number): string {
  if (bytes === 0) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return `${Math.floor(diff / 86_400_000)}d ago`;
}

export default function DataExportCard({ exports: exps, appName }: DataExportCardProps) {
  const activeCount = exps.filter(
    (e) => e.status === "pending" || e.status === "processing",
  ).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Data Exports</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {activeCount > 0 && (
          <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
            {activeCount} in progress
          </span>
        )}
      </div>

      {exps.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No exports</p>
      ) : (
        <div className="space-y-2.5">
          {exps.map((exp) => {
            const st = STATUS_STYLES[exp.status] ?? STATUS_STYLES.pending;
            return (
              <div
                key={exp.export_id}
                className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2.5 dark:border-gray-800"
              >
                <div className="flex items-center gap-2.5">
                  <span>{st.icon}</span>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                        {exp.resource_type}
                      </span>
                      <span
                        className={`rounded px-1.5 py-0.5 text-[10px] font-medium uppercase ${
                          FORMAT_BADGES[exp.format] ?? FORMAT_BADGES.json
                        }`}
                      >
                        {exp.format}
                      </span>
                    </div>
                    <div className="mt-0.5 flex items-center gap-2 text-[11px] text-gray-400">
                      <span>{timeAgo(exp.created_at)}</span>
                      {exp.status === "completed" && (
                        <>
                          <span>·</span>
                          <span>{exp.row_count.toLocaleString()} rows</span>
                          <span>·</span>
                          <span>{formatBytes(exp.file_size_bytes)}</span>
                        </>
                      )}
                      {exp.status === "failed" && exp.error_message && (
                        <>
                          <span>·</span>
                          <span className="text-red-500">{exp.error_message}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <span className={`text-xs font-medium capitalize ${st.text}`}>{exp.status}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
