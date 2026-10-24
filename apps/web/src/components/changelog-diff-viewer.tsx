"use client";

interface ChangeEntry { type?: string; description: string; breaking?: boolean; }
interface ChangelogDiffViewerProps { added: ChangeEntry[]; removed: ChangeEntry[];
  netChange: number; }

export function ChangelogDiffViewer({ added, removed, netChange }: ChangelogDiffViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Changelog Diff</h3>
        <span className="text-xs text-gray-400">
          +{added.length} / -{removed.length} (net {netChange >= 0 ? "+" : ""}{netChange})
        </span>
      </div>
      {added.length > 0 && (
        <div className="border-b dark:border-gray-700">
          <div className="px-4 py-1.5 text-[10px] text-green-600 font-medium bg-green-50/50 dark:bg-green-900/5">Added</div>
          {added.map((e, i) => (
            <div key={i} className="px-4 py-1.5 text-xs text-green-700 dark:text-green-400">
              + {e.description} {e.breaking && <span className="text-red-500 text-[10px]">⚠ breaking</span>}
            </div>
          ))}
        </div>
      )}
      {removed.length > 0 && (
        <div>
          <div className="px-4 py-1.5 text-[10px] text-red-600 font-medium bg-red-50/50 dark:bg-red-900/5">Removed</div>
          {removed.map((e, i) => (
            <div key={i} className="px-4 py-1.5 text-xs text-red-700 dark:text-red-400">- {e.description}</div>
          ))}
        </div>
      )}
    </div>
  );
}
