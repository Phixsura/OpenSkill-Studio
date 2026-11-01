"use client";

interface ExportFormatInfo {
  format: string;
  entry_count: number;
  size_bytes: number;
  available: boolean;
}

interface ChangelogExportCardProps {
  formats: ExportFormatInfo[];
  appName: string;
}

const FORMAT_ICONS: Record<string, string> = {
  markdown: "📝",
  json: "📋",
  csv: "📊",
};

function formatSize(bytes: number): string {
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${bytes} B`;
}

export default function ChangelogExportCard({ formats, appName }: ChangelogExportCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Export Changelog
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
      </div>

      {formats.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No export formats</p>
      ) : (
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
          {formats.map((f) => (
            <div
              key={f.format}
              className={`rounded-lg border px-3 py-3 text-center ${
                f.available
                  ? "border-gray-200 dark:border-gray-700"
                  : "border-gray-100 opacity-50 dark:border-gray-800"
              }`}
            >
              <span className="text-2xl">{FORMAT_ICONS[f.format] ?? "📄"}</span>
              <p className="mt-1 text-sm font-medium capitalize text-gray-800 dark:text-gray-200">
                {f.format}
              </p>
              <p className="text-[11px] text-gray-400">
                {f.entry_count} entries · {formatSize(f.size_bytes)}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
