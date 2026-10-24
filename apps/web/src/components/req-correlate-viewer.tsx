"use client";

interface Hop { service: string; method: string; path: string; status: number; durationMs: number; }
interface ReqCorrelateViewerProps { correlationId: string; hops: Hop[];
  totalMs: number; success: boolean; }

export function ReqCorrelateViewer({ correlationId, hops, totalMs, success }: ReqCorrelateViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Request Trace</h3>
        <span className={`text-xs font-bold ${success ? "text-green-600" : "text-red-500"}`}>
          {success ? "✅" : "❌"} {totalMs}ms · {hops.length} hops
        </span>
      </div>
      <div className="px-4 py-2 text-[10px] text-gray-400 font-mono">{correlationId}</div>
      <div className="border-t dark:border-gray-700 divide-y dark:divide-gray-700">
        {hops.map((h, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-1.5 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-gray-400 w-4">{i + 1}.</span>
              <span className="font-semibold">{h.service}</span>
              <span className="text-gray-400">{h.method} {h.path}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className={h.status >= 400 ? "text-red-500" : "text-green-600"}>{h.status}</span>
              <span className="text-gray-400">{h.durationMs}ms</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
