"use client";

interface LogExportConfigCardProps {
  destination: string; endpointUrl: string; status: string; format: string;
  filters: string[]; onTest: () => void; onDisable: () => void;
}

const DEST_ICONS: Record<string, string> = {
  datadog: "🐕", splunk: "⚡", elasticsearch: "🔍", cloudwatch: "☁️", grafana_loki: "📊",
};

export function LogExportConfigCard({ destination, endpointUrl, status, format, filters, onTest, onDisable }: LogExportConfigCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">{DEST_ICONS[destination] || "📤"}</span>
          <div>
            <h3 className="font-semibold capitalize">{destination}</h3>
            <p className="text-xs text-gray-400">{endpointUrl}</p>
          </div>
        </div>
        <span className={`rounded-full px-2 py-0.5 text-xs ${status === "configured" ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"}`}>
          {status}
        </span>
      </div>
      <div className="mt-2 flex gap-1">
        <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-700">Format: {format}</span>
        <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-700">Filters: {filters.join(", ")}</span>
      </div>
      <div className="mt-3 flex gap-2">
        <button onClick={onTest} className="rounded bg-blue-600 px-3 py-1 text-xs text-white">Test</button>
        <button onClick={onDisable} className="rounded border px-3 py-1 text-xs text-red-600">Disable</button>
      </div>
    </div>
  );
}
