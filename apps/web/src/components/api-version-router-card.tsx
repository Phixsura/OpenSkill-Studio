"use client";

interface APIVersionInfo {
  version: string;
  status: "active" | "deprecated" | "sunset";
  base_path: string;
  is_default: boolean;
  sunset_date: string;
}

interface APIVersionRouterCardProps {
  versions: APIVersionInfo[];
  appName: string;
}

const STATUS_STYLES: Record<string, { bg: string; text: string }> = {
  active: { bg: "bg-green-100 dark:bg-green-900/30", text: "text-green-700 dark:text-green-400" },
  deprecated: {
    bg: "bg-yellow-100 dark:bg-yellow-900/30",
    text: "text-yellow-700 dark:text-yellow-400",
  },
  sunset: { bg: "bg-red-100 dark:bg-red-900/30", text: "text-red-700 dark:text-red-400" },
};

export default function APIVersionRouterCard({ versions, appName }: APIVersionRouterCardProps) {
  const activeCount = versions.filter((v) => v.status === "active").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">API Versions</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{activeCount} active</span>
      </div>

      {versions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No API versions</p>
      ) : (
        <div className="space-y-2">
          {versions.map((v) => {
            const st = STATUS_STYLES[v.status] ?? STATUS_STYLES.active;
            return (
              <div
                key={v.version}
                className={`flex items-center justify-between rounded-lg border px-3 py-2 ${
                  v.status === "sunset"
                    ? "border-red-200 opacity-50 dark:border-red-900/50"
                    : "border-gray-100 dark:border-gray-800"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="font-mono text-sm font-medium text-gray-800 dark:text-gray-200">
                    {v.version}
                  </span>
                  <span
                    className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${st.bg} ${st.text}`}
                  >
                    {v.status}
                  </span>
                  {v.is_default && (
                    <span className="text-[10px] text-blue-600 dark:text-blue-400">default</span>
                  )}
                </div>
                <div className="text-[11px] text-gray-400">
                  <span className="font-mono">{v.base_path}</span>
                  {v.sunset_date && <span className="ml-2">sunset {v.sunset_date}</span>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
