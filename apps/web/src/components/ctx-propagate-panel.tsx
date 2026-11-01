"use client";
interface CtxInfo { requestId: string; traceId: string; userId: string; baggage: Record<string, string>; }
interface CtxPropagatePanelProps { contexts: CtxInfo[]; activeCount: number; }
export function CtxPropagatePanel({ contexts, activeCount }: CtxPropagatePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔗 Context Propagation</h3>
        <span className="text-xs text-gray-400">{activeCount} active</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {contexts.map(c => (
          <div key={c.requestId} className="px-4 py-1.5 text-xs">
            <div className="font-mono text-blue-500">{c.requestId}</div>
            <div className="text-gray-400">{c.traceId} · {c.userId}
              {Object.keys(c.baggage).length > 0 && ` · ${Object.entries(c.baggage).map(([k,v]) => `${k}=${v}`).join(", ")}`}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
