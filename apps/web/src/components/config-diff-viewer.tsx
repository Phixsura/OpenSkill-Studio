"use client";

interface ConfigDiff {
  key: string;
  status: "added" | "removed" | "changed" | "unchanged";
  oldValue?: string;
  newValue?: string;
}

export function ConfigDiffViewer({
  diffs,
  fromVersion,
  toVersion,
  onApply,
  onRevert,
}: {
  diffs: ConfigDiff[];
  fromVersion: string;
  toVersion: string;
  onApply?: () => void;
  onRevert?: () => void;
}) {
  const added = diffs.filter((d) => d.status === "added");
  const removed = diffs.filter((d) => d.status === "removed");
  const changed = diffs.filter((d) => d.status === "changed");
  const unchanged = diffs.filter((d) => d.status === "unchanged");

  const statusStyle: Record<string, { bg: string; icon: string; label: string }> = {
    added: { bg: "bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-800", icon: "+", label: "Added" },
    removed: { bg: "bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800", icon: "−", label: "Removed" },
    changed: { bg: "bg-yellow-50 dark:bg-yellow-900/10 border-yellow-200 dark:border-yellow-800", icon: "~", label: "Changed" },
    unchanged: { bg: "bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700", icon: "=", label: "Unchanged" },
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📝 Config Changes</h2>
        <div className="text-sm text-gray-500">
          {fromVersion} → {toVersion}
        </div>
      </div>

      <div className="flex gap-3 text-xs">
        <span className="text-green-600">+{added.length} added</span>
        <span className="text-red-600">−{removed.length} removed</span>
        <span className="text-yellow-600">~{changed.length} changed</span>
        <span className="text-gray-400">={unchanged.length} unchanged</span>
      </div>

      <div className="space-y-1">
        {diffs.filter((d) => d.status !== "unchanged").map((diff) => {
          const style = statusStyle[diff.status];
          return (
            <div key={diff.key} className={`rounded-lg border p-3 ${style.bg}`}>
              <div className="flex items-center gap-2 text-sm">
                <span className="font-mono font-bold w-4">{style.icon}</span>
                <span className="font-mono font-medium">{diff.key}</span>
                <span className="text-xs text-gray-400">{style.label}</span>
              </div>
              {diff.status === "changed" && (
                <div className="ml-6 mt-1 text-xs font-mono space-y-0.5">
                  <div className="text-red-500">- {diff.oldValue}</div>
                  <div className="text-green-500">+ {diff.newValue}</div>
                </div>
              )}
              {diff.status === "added" && (
                <div className="ml-6 mt-1 text-xs font-mono text-green-500">+ {diff.newValue}</div>
              )}
              {diff.status === "removed" && (
                <div className="ml-6 mt-1 text-xs font-mono text-red-500">- {diff.oldValue}</div>
              )}
            </div>
          );
        })}
      </div>

      {(onApply || onRevert) && (
        <div className="flex gap-2">
          {onApply && (
            <button onClick={onApply} className="rounded-lg bg-green-600 text-white px-4 py-2 text-sm font-medium">
              ✅ Apply Changes
            </button>
          )}
          {onRevert && (
            <button onClick={onRevert} className="rounded-lg border dark:border-gray-600 px-4 py-2 text-sm font-medium">
              ↩️ Revert
            </button>
          )}
        </div>
      )}
    </div>
  );
}
