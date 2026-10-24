"use client";

interface ResLifecyclePanelProps { total: number; active: number; expired: number;
  orphaned: number; needsCleanup: number; byType: Record<string, number>; }

export function ResLifecyclePanel({ total, active, expired, orphaned, needsCleanup, byType }: ResLifecyclePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">♻️ Resource Lifecycle</h3>
        <span className="text-xs text-gray-400">{total} resources{needsCleanup > 0 ? ` · ⚠ ${needsCleanup} cleanup` : ""}</span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        {[{ l: "Active", v: active, c: "text-green-600" }, { l: "Expired", v: expired, c: "text-red-500" },
          { l: "Orphaned", v: orphaned, c: "text-yellow-600" }, { l: "Types", v: Object.keys(byType).length, c: "" }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-2 text-center">
            <div className={`text-sm font-bold ${s.c}`}>{s.v}</div>
            <div className="text-[9px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
