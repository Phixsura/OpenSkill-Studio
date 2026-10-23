"use client";

interface ContentFlag { word: string; severity: string; }
interface ContentFilterBadgeProps { safe: boolean; maxSeverity: string; flagCount: number; flags: ContentFlag[]; }

const severityColors: Record<string, string> = {
  none: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  critical: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
};

export function ContentFilterBadge({ safe, maxSeverity, flagCount, flags }: ContentFilterBadgeProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <span className={`rounded px-2 py-0.5 text-xs font-medium ${severityColors[maxSeverity] ?? severityColors.none}`}>
          {safe ? "✓ Safe" : `⚠ ${flagCount} issue${flagCount !== 1 ? "s" : ""}`}
        </span>
        {!safe && <span className="text-xs text-gray-400 capitalize">{maxSeverity} severity</span>}
      </div>
      {flags.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {flags.map((f, i) => (
            <span key={i} className="rounded bg-red-50 px-1.5 py-0.5 text-xs text-red-600 dark:bg-red-900/20 dark:text-red-400">
              {f.word}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
