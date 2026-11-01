"use client";

interface VersionInfo {
  version: string;
  status: "draft" | "active" | "deprecated" | "sunset";
  endpoint_count: number;
}

interface APIVersioningCardProps {
  versions: VersionInfo[];
  appName: string;
}

const statusStyle: Record<string, string> = {
  draft: "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400",
  active: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  deprecated: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
  sunset: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
};

export default function APIVersioningCard({ versions, appName }: APIVersioningCardProps) {
  const active = versions.filter((v) => v.status === "active").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🏷️ API Versions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{active} active / {versions.length} total</span>
      </div>

      {versions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No API versions</p>
      ) : (
        <div className="space-y-1.5">
          {versions.map((v) => (
            <div key={v.version} className="flex items-center justify-between rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-medium text-gray-800 dark:text-gray-200">{v.version}</span>
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${statusStyle[v.status]}`}>{v.status}</span>
              </div>
              <span className="text-[10px] text-gray-400">{v.endpoint_count} endpoints</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
