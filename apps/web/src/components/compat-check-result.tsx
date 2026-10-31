"use client";

interface Change { type: string; path: string; method?: string; }
interface CompatCheckResultProps { compatible: boolean; breakingChanges: Change[];
  compatibleChanges: Change[]; }

export function CompatCheckResult({ compatible, breakingChanges, compatibleChanges }: CompatCheckResultProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`flex items-center justify-between p-4 border-b dark:border-gray-700 ${compatible ? "bg-green-50 dark:bg-green-900/10" : "bg-red-50 dark:bg-red-900/10"}`}>
        <h3 className="font-semibold text-sm">🔄 API Compatibility</h3>
        <span className={`text-xs font-medium ${compatible ? "text-green-600" : "text-red-500"}`}>
          {compatible ? "✅ Backward Compatible" : `⚠ ${breakingChanges.length} Breaking Changes`}
        </span>
      </div>
      {breakingChanges.length > 0 && (
        <div className="border-b dark:border-gray-700">
          <div className="px-4 py-1.5 text-[10px] text-red-600 font-medium">Breaking</div>
          {breakingChanges.map((c, i) => (
            <div key={i} className="px-4 py-1 text-xs text-red-600">✗ {c.type}: {c.path}{c.method ? ` ${c.method}` : ""}</div>
          ))}
        </div>
      )}
      {compatibleChanges.length > 0 && (
        <div>
          <div className="px-4 py-1.5 text-[10px] text-green-600 font-medium">Compatible</div>
          {compatibleChanges.map((c, i) => (
            <div key={i} className="px-4 py-1 text-xs text-green-600">✓ {c.type}: {c.path}</div>
          ))}
        </div>
      )}
    </div>
  );
}
