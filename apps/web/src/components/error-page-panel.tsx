"use client";
interface ErrorCodeCount { code: string; count: number; }
interface ErrorPagePanelProps { total: number; byCode: ErrorCodeCount[]; mostCommon: string; }
export function ErrorPagePanel({ total, byCode, mostCommon }: ErrorPagePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">❌ Error Summary</h3>
        <span className="text-xs text-gray-400">{total} errors · most: {mostCommon}</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {byCode.map(e => (
          <div key={e.code} className="flex justify-between px-4 py-1.5 text-xs">
            <span className="font-mono text-red-500">{e.code}</span>
            <span className="text-gray-400">{e.count}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
