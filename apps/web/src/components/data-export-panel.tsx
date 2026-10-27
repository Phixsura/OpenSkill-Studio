"use client";

import { useState } from "react";

interface ExportJob {
  job_id: string;
  status: "requested" | "processing" | "ready" | "downloaded" | "expired" | "failed";
  export_format: "json" | "csv";
  row_count: number;
  byte_size: number;
  requested_at: string;
  completed_at: string | null;
  error: string | null;
}

interface DataExportPanelProps {
  jobs: ExportJob[];
  onRequestExport: (format: "json" | "csv", redactPii: boolean) => void;
  onDownload: (jobId: string) => void;
  exporting?: boolean;
}

const STATUS_STYLES: Record<string, { label: string; color: string }> = {
  requested: {
    label: "Queued",
    color: "text-blue-600 bg-blue-100 dark:bg-blue-900/30 dark:text-blue-300",
  },
  processing: {
    label: "Processing",
    color: "text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30 dark:text-yellow-300",
  },
  ready: {
    label: "Ready",
    color: "text-green-600 bg-green-100 dark:bg-green-900/30 dark:text-green-300",
  },
  downloaded: {
    label: "Downloaded",
    color: "text-gray-600 bg-gray-100 dark:bg-gray-800 dark:text-gray-400",
  },
  expired: {
    label: "Expired",
    color: "text-gray-400 bg-gray-100 dark:bg-gray-800 dark:text-gray-500",
  },
  failed: {
    label: "Failed",
    color: "text-red-600 bg-red-100 dark:bg-red-900/30 dark:text-red-300",
  },
};

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1048576).toFixed(1)} MB`;
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function DataExportPanel({
  jobs,
  onRequestExport,
  onDownload,
  exporting,
}: DataExportPanelProps) {
  const [format, setFormat] = useState<"json" | "csv">("json");
  const [redactPii, setRedactPii] = useState(true);

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <h3 className="font-semibold">Data Export</h3>
        <p className="text-xs text-gray-500">{jobs.length} exports</p>
      </div>

      {/* New export form */}
      <div className="flex items-center gap-3 border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <select
          value={format}
          onChange={(e) => setFormat(e.target.value as "json" | "csv")}
          className="rounded border border-gray-300 px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800"
          aria-label="Export format"
        >
          <option value="json">JSON</option>
          <option value="csv">CSV</option>
        </select>
        <label className="flex items-center gap-1.5 text-xs">
          <input
            type="checkbox"
            checked={redactPii}
            onChange={(e) => setRedactPii(e.target.checked)}
            className="rounded"
          />
          Redact PII
        </label>
        <button
          onClick={() => onRequestExport(format, redactPii)}
          disabled={exporting}
          className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {exporting ? "Exporting…" : "Export"}
        </button>
      </div>

      {/* Job list */}
      {jobs.length === 0 ? (
        <div className="py-8 text-center">
          <span className="text-3xl">📤</span>
          <p className="mt-2 text-sm text-gray-500">No exports yet</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-100 dark:divide-gray-800">
          {jobs.map((j) => {
            const st = STATUS_STYLES[j.status] ?? STATUS_STYLES.failed;
            return (
              <div key={j.job_id} className="flex items-center justify-between px-4 py-2.5">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${st.color}`}>
                      {st.label}
                    </span>
                    <span className="text-xs font-medium uppercase">{j.export_format}</span>
                    {j.row_count > 0 && (
                      <span className="text-xs text-gray-400">
                        {j.row_count.toLocaleString()} rows • {formatBytes(j.byte_size)}
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-gray-400">
                    {formatDate(j.requested_at)}
                    {j.error && <span className="ml-1 text-red-500">— {j.error}</span>}
                  </p>
                </div>
                {j.status === "ready" && (
                  <button
                    onClick={() => onDownload(j.job_id)}
                    className="rounded-md border border-green-300 px-2.5 py-1 text-xs font-medium text-green-600 hover:bg-green-50 dark:border-green-700 dark:text-green-400"
                  >
                    Download
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
