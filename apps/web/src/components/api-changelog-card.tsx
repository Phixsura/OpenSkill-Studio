"use client";

interface EndpointChangeInfo {
  method: string;
  path: string;
  change_type: "added" | "modified" | "removed" | "deprecated";
  breaking: boolean;
  description: string;
}

interface APIChangelogCardProps {
  fromVersion: string;
  toVersion: string;
  changes: EndpointChangeInfo[];
  appName: string;
}

const CHANGE_STYLES: Record<string, { icon: string; text: string }> = {
  added: { icon: "+", text: "text-green-600 dark:text-green-400" },
  modified: { icon: "~", text: "text-blue-600 dark:text-blue-400" },
  removed: { icon: "−", text: "text-red-600 dark:text-red-400" },
  deprecated: { icon: "⚠", text: "text-yellow-600 dark:text-yellow-400" },
};

const METHOD_COLORS: Record<string, string> = {
  GET: "text-green-700 bg-green-100 dark:text-green-400 dark:bg-green-900/30",
  POST: "text-blue-700 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30",
  PUT: "text-yellow-700 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30",
  DELETE: "text-red-700 bg-red-100 dark:text-red-400 dark:bg-red-900/30",
};

export default function APIChangelogCard({
  fromVersion,
  toVersion,
  changes,
  appName,
}: APIChangelogCardProps) {
  const breakingCount = changes.filter((c) => c.breaking).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">API Changes</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs text-gray-500">
            {fromVersion} → {toVersion}
          </span>
          {breakingCount > 0 && (
            <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
              {breakingCount} breaking
            </span>
          )}
        </div>
      </div>

      {changes.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No endpoint changes</p>
      ) : (
        <div className="space-y-1">
          {changes.map((c, i) => {
            const st = CHANGE_STYLES[c.change_type] ?? CHANGE_STYLES.modified;
            return (
              <div
                key={i}
                className="flex items-center gap-2 rounded px-2 py-1 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <span className={`text-sm font-bold ${st.text}`}>{st.icon}</span>
                <span
                  className={`rounded px-1 py-0.5 text-[9px] font-bold ${METHOD_COLORS[c.method] ?? "bg-gray-100 text-gray-600"}`}
                >
                  {c.method}
                </span>
                <span className="font-mono text-xs text-gray-700 dark:text-gray-300">{c.path}</span>
                {c.breaking && <span className="text-[9px] text-red-500">BREAKING</span>}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
