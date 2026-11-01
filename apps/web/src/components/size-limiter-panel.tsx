"use client";
interface SizeLimiterPanelProps { maxBytes: number; humanLimit: string;
  accepted: number; rejected: number; total: number; }
export function SizeLimiterPanel({ humanLimit, accepted, rejected, total }: SizeLimiterPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📏 Size Limiter</h3>
        <span className="text-xs text-gray-400">max {humanLimit} · {total} checked</span>
      </div>
      <div className="grid grid-cols-2 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Accepted</span><div className="font-bold text-green-600 text-lg">{accepted}</div></div>
        <div><span className="text-gray-400">Rejected</span><div className={`font-bold text-lg ${rejected > 0 ? "text-red-500" : "text-gray-400"}`}>{rejected}</div></div>
      </div>
    </div>
  );
}
