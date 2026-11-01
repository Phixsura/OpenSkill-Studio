"use client";

interface ErrorCodeInfo {
  code: string;
  message: string;
  http_status: number;
  category: string;
  retryable: boolean;
}

interface APIErrorCodeCardProps {
  codes: ErrorCodeInfo[];
  appName: string;
}

export default function APIErrorCodeCard({ codes, appName }: APIErrorCodeCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">❌ Error Codes</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{codes.length} codes</span>
      </div>

      {codes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No error codes defined</p>
      ) : (
        <div className="space-y-1">
          {codes.map((c) => (
            <div key={c.code} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-medium text-gray-800 dark:text-gray-200">{c.code}</span>
                <span className={`text-[10px] ${c.http_status >= 500 ? "text-red-500" : "text-yellow-600"}`}>{c.http_status}</span>
                {c.retryable && <span className="text-[9px] text-blue-500">retryable</span>}
              </div>
              <span className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800">{c.category}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
