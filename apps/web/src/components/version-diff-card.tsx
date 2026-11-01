"use client";

interface FieldChange {
  path: string;
  change_type: "added" | "removed" | "modified";
  old_value?: unknown;
  new_value?: unknown;
}

interface VersionDiffCardProps {
  fromVersion: string;
  toVersion: string;
  changes: FieldChange[];
  appName: string;
}

const CHANGE_STYLES: Record<string, { icon: string; bg: string; text: string }> = {
  added: {
    icon: "+",
    bg: "bg-green-50 dark:bg-green-950/20",
    text: "text-green-700 dark:text-green-400",
  },
  removed: {
    icon: "−",
    bg: "bg-red-50 dark:bg-red-950/20",
    text: "text-red-700 dark:text-red-400",
  },
  modified: {
    icon: "~",
    bg: "bg-blue-50 dark:bg-blue-950/20",
    text: "text-blue-700 dark:text-blue-400",
  },
};

function formatValue(v: unknown): string {
  if (v === null || v === undefined) return "null";
  if (typeof v === "string") return `"${v}"`;
  return JSON.stringify(v);
}

export default function VersionDiffCard({
  fromVersion,
  toVersion,
  changes,
  appName,
}: VersionDiffCardProps) {
  const added = changes.filter((c) => c.change_type === "added").length;
  const removed = changes.filter((c) => c.change_type === "removed").length;
  const modified = changes.filter((c) => c.change_type === "modified").length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Version Diff</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="font-mono text-xs text-gray-500">
          {fromVersion} → {toVersion}
        </span>
      </div>

      {/* Summary */}
      <div className="mb-3 flex items-center gap-3 text-xs">
        {added > 0 && <span className="text-green-600 dark:text-green-400">+{added} added</span>}
        {removed > 0 && <span className="text-red-600 dark:text-red-400">−{removed} removed</span>}
        {modified > 0 && (
          <span className="text-blue-600 dark:text-blue-400">~{modified} modified</span>
        )}
        {changes.length === 0 && <span className="text-gray-400">No changes</span>}
      </div>

      {/* Change list */}
      {changes.length > 0 && (
        <div className="space-y-1">
          {changes.map((c) => {
            const st = CHANGE_STYLES[c.change_type] ?? CHANGE_STYLES.modified;
            return (
              <div key={c.path} className={`flex items-start gap-2 rounded px-2.5 py-1.5 ${st.bg}`}>
                <span className={`mt-0.5 font-mono text-xs font-bold ${st.text}`}>{st.icon}</span>
                <div className="min-w-0 flex-1">
                  <span className="font-mono text-xs font-medium text-gray-800 dark:text-gray-200">
                    {c.path}
                  </span>
                  {c.change_type === "modified" && (
                    <p className="mt-0.5 font-mono text-[10px] text-gray-500">
                      {formatValue(c.old_value)} → {formatValue(c.new_value)}
                    </p>
                  )}
                  {c.change_type === "added" && (
                    <p className="mt-0.5 font-mono text-[10px] text-green-600/70">
                      {formatValue(c.new_value)}
                    </p>
                  )}
                  {c.change_type === "removed" && (
                    <p className="mt-0.5 font-mono text-[10px] text-red-600/70">
                      {formatValue(c.old_value)}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
