"use client";

interface ErrorClassificationPanelProps { total: number; byCategory: Record<string, number>;
  bySeverity: Record<string, number>; hasCritical: boolean; }

const SEV_COLORS: Record<string, string> = {
  critical: "bg-red-500", high: "bg-orange-500", medium: "bg-yellow-500", low: "bg-blue-500",
};

export function ErrorClassificationPanel({ total, byCategory, bySeverity, hasCritical }: ErrorClassificationPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🐛 Error Classification</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-gray-400">{total} errors</span>
          {hasCritical && <span className="text-red-500 font-medium">⚠ Critical</span>}
        </div>
      </div>
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700">
        <div className="p-4">
          <div className="text-xs text-gray-400 mb-2">By Category</div>
          {Object.entries(byCategory).map(([cat, count]) => (
            <div key={cat} className="flex justify-between text-xs py-0.5">
              <span className="capitalize">{cat.replaceAll("_", " ")}</span>
              <span className="text-gray-400">{count}</span>
            </div>
          ))}
        </div>
        <div className="p-4">
          <div className="text-xs text-gray-400 mb-2">By Severity</div>
          {Object.entries(bySeverity).map(([sev, count]) => (
            <div key={sev} className="flex items-center gap-2 text-xs py-0.5">
              <span className={`w-2 h-2 rounded-full ${SEV_COLORS[sev] ?? "bg-gray-400"}`} />
              <span className="capitalize">{sev}</span>
              <span className="text-gray-400 ml-auto">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
