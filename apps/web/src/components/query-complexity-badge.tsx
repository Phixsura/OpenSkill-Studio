"use client";

interface QueryComplexityBadgeProps { complexity: number; maxComplexity: number;
  depth: number; maxDepth: number; allowed: boolean; fields: number; lists: number; }

export function QueryComplexityBadge({ complexity, maxComplexity, depth, maxDepth, allowed, fields, lists }: QueryComplexityBadgeProps) {
  const pct = Math.min(Math.round((complexity / maxComplexity) * 100), 100);
  return (
    <div className="rounded-xl border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold">Query Complexity</h4>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${allowed ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
          {allowed ? "✅ Allowed" : "❌ Rejected"}
        </span>
      </div>
      <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full mb-2 overflow-hidden">
        <div className={`h-full rounded-full ${pct > 80 ? "bg-red-500" : pct > 50 ? "bg-yellow-500" : "bg-green-500"}`}
             style={{ width: `${pct}%` }} />
      </div>
      <div className="flex gap-4 text-xs text-gray-400">
        <span>Cost: {complexity}/{maxComplexity}</span>
        <span>Depth: {depth}/{maxDepth}</span>
        <span>{fields} fields</span>
        <span>{lists} lists</span>
      </div>
    </div>
  );
}
