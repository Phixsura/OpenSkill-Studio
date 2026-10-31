"use client";

interface LogPattern { pattern: string; count: number; pct: number; }
interface LogPatternViewerProps { patterns: LogPattern[]; totalLines: number;
  uniquePatterns: number; compressionRatio: number; }

export function LogPatternViewer({ patterns, totalLines, uniquePatterns, compressionRatio }: LogPatternViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔍 Log Patterns</h3>
        <span className="text-xs text-gray-400">{totalLines} lines → {uniquePatterns} patterns ({compressionRatio}%)</span>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-40 overflow-y-auto">
        {patterns.map((p, i) => (
          <div key={i} className="px-4 py-1.5 text-xs">
            <div className="flex justify-between mb-0.5">
              <span className="font-mono truncate max-w-[250px]">{p.pattern}</span>
              <span className="text-gray-400 ml-2">{p.count}× ({p.pct}%)</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
