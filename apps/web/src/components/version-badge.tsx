"use client";

interface VersionBadgeProps { version: string; isStable: boolean; prerelease: string | null;
  showBump?: boolean; onBump?: (type: "major" | "minor" | "patch") => void; }

export function VersionBadge({ version, isStable, prerelease, showBump, onBump }: VersionBadgeProps) {
  return (
    <div className="flex items-center gap-2">
      <span className={`rounded px-2 py-0.5 text-sm font-mono font-medium ${isStable ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"}`}>
        v{version}
      </span>
      {prerelease && <span className="text-xs text-gray-400">{prerelease}</span>}
      {isStable && <span className="text-xs text-green-600">Stable</span>}
      {showBump && onBump && (
        <div className="flex gap-1">
          {(["patch", "minor", "major"] as const).map(t => (
            <button key={t} onClick={() => onBump(t)}
              className="rounded bg-gray-100 px-1.5 py-0.5 text-xs capitalize hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700">
              {t}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
