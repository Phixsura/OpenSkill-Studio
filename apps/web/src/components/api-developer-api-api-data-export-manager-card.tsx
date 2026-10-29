"use client";

interface JobInfo { job_id: string; export_type: string; format: string; status: string; row_count: number; file_size_bytes: number; }
interface Props { jobs: JobInfo[]; appName: string; }

const sDot: Record<string, string> = { pending: "bg-gray-400", running: "bg-blue-500", completed: "bg-green-500", failed: "bg-red-500" };

function fmtSize(b: number) { return b < 1024 ? `${b}B` : b < 1048576 ? `${(b/1024).toFixed(1)}KB` : `${(b/1048576).toFixed(1)}MB`; }

export default function APIDeveloperAPIApiDataExportManagerCard({ jobs, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📤 Data Exports</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {jobs.length} jobs</p>
      </div>
      {jobs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No export jobs</p>
      ) : (
        <div className="space-y-1.5">
          {jobs.map((j) => (
            <div key={j.job_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`h-1.5 w-1.5 rounded-full ${sDot[j.status] ?? "bg-gray-400"}`} />
                <span className="text-gray-700 dark:text-gray-300">{j.export_type}</span>
                <span className="text-[9px] text-gray-400">.{j.format}</span>
              </div>
              <span className="text-gray-400">{j.row_count > 0 ? `${j.row_count.toLocaleString()} rows · ${fmtSize(j.file_size_bytes)}` : j.status}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
