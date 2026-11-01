"use client";

interface TraceContextViewerProps { traceId: string; spanId: string;
  parentId: string | null; operation: string; sampled: boolean;
  header: string; childCount: number; }

export function TraceContextViewer({ traceId, spanId, parentId, operation, sampled, header, childCount }: TraceContextViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold text-sm">🔍 Trace Context</h3>
        <span className={`text-xs ${sampled ? "text-green-600" : "text-gray-400"}`}>
          {sampled ? "● Sampled" : "○ Not Sampled"}
        </span>
      </div>
      <div className="p-3 space-y-1 text-xs font-mono">
        <div><span className="text-gray-400">trace_id:</span> {traceId}</div>
        <div><span className="text-gray-400">span_id:</span> {spanId}</div>
        {parentId && <div><span className="text-gray-400">parent:</span> {parentId}</div>}
        <div><span className="text-gray-400">operation:</span> {operation}</div>
      </div>
      <div className="px-3 py-2 border-t dark:border-gray-700 text-[10px] text-gray-400 font-mono break-all">
        traceparent: {header}
      </div>
    </div>
  );
}
