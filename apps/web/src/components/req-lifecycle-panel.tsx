"use client";
interface Stage { stage: string; durationMs: number; status: string; }
interface ReqLifecyclePanelProps { requestId: string; stages: Stage[]; totalMs: number; success: boolean; }
export function ReqLifecyclePanel({ requestId, stages, totalMs, success }: ReqLifecyclePanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Request Lifecycle</h3>
        <span className={`text-xs font-bold ${success ? "text-green-600" : "text-red-500"}`}>
          {requestId} · {totalMs}ms · {success ? "✅" : "❌"}
        </span>
      </div>
      <div className="p-4 flex items-center gap-0.5">
        {stages.map((s, i) => {
          const widthPct = Math.max(s.durationMs / totalMs * 100, 5);
          return (
            <div key={i} className="flex flex-col items-center" style={{ width: `${widthPct}%` }}>
              <div className={`w-full h-4 rounded ${s.status === "error" ? "bg-red-500" : "bg-blue-500"}`}
                title={`${s.stage}: ${s.durationMs}ms`} />
              <span className="text-[8px] text-gray-400 mt-0.5 truncate w-full text-center">{s.stage}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
