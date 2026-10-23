"use client";

interface Version { version: string; publishedAt: string; isCurrent: boolean;
  isPrerelease: boolean; compatible: boolean; downloads: number; }
interface VersionSelectorDropdownProps { versions: Version[]; current: string;
  latestStable: string | null; onSelect: (version: string) => void; }

export function VersionSelectorDropdown({ versions, current, latestStable, onSelect }: VersionSelectorDropdownProps) {
  return (
    <div className="space-y-2">
      <label className="block text-xs text-gray-400">Version</label>
      <select value={current} onChange={e => onSelect(e.target.value)}
        className="w-full rounded border px-3 py-2 text-sm font-mono dark:bg-gray-800 dark:border-gray-600">
        {versions.map(v => (
          <option key={v.version} value={v.version} disabled={!v.compatible}>
            {v.version}{v.isCurrent ? " (current)" : ""}{v.isPrerelease ? " [pre]" : ""}
            {!v.compatible ? " ⚠ incompatible" : ""}
          </option>
        ))}
      </select>
      {latestStable && current !== latestStable && (
        <p className="text-xs text-blue-600">Latest stable: {latestStable}</p>
      )}
    </div>
  );
}
