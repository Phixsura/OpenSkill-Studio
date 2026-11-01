"use client";

interface LogAggregationViewProps { totalLines: number; sourceCount: number;
  errorCount: number; errorRate: number; byLevel: Record<string, number>;
  bySource: Record<string, number>; }

export function LogAggregationView({ totalLines, sourceCount, errorCount, errorRate, byLevel, bySource }: LogAggregationViewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Log Aggregation</h3>
        <span className="text-xs text-gray-400">{totalLines.toLocaleString()} lines · {sourceCount} sources</span>
      </div>
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700 p-3 text-xs">
        <div>
          <div className="text-gray-400 mb-1">By Level</div>
          {Object.entries(byLevel).map(([lv, c]) => (
            <div key={lv} className="flex justify-between py-0.5">
              <span className={lv === "error" ? "text-red-500" : ""}>{lv}</span>
              <span className="text-gray-400">{c}</span>
            </div>
          ))}
        </div>
        <div className="pl-3">
          <div className="text-gray-400 mb-1">By Source</div>
          {Object.entries(bySource).map(([src, c]) => (
            <div key={src} className="flex justify-between py-0.5">
              <span>{src}</span><span className="text-gray-400">{c}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="p-3 border-t dark:border-gray-700 text-xs text-gray-400">
        Errors: {errorCount} ({errorRate}%)
      </div>
    </div>
  );
}
