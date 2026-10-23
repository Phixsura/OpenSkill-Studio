"use client";

interface ActionItem { task: string; done: boolean; }
interface PostmortemViewerProps { incidentId: string; title: string; severity: string;
  rootCause: string; actionItems: ActionItem[]; progressPct: number; }

const SEV_COLORS: Record<string, string> = {
  critical: "bg-red-500", major: "bg-orange-500", minor: "bg-yellow-500",
};

export function PostmortemViewer({ incidentId, title, severity, rootCause, actionItems, progressPct }: PostmortemViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 text-[10px] text-white rounded ${SEV_COLORS[severity] ?? "bg-gray-500"}`}>{severity}</span>
          <h3 className="font-semibold text-sm">{title}</h3>
        </div>
        <div className="text-[10px] text-gray-400 mt-0.5">{incidentId}</div>
      </div>
      <div className="p-3 border-b dark:border-gray-700">
        <div className="text-xs text-gray-400">Root Cause</div>
        <div className="text-sm mt-0.5">{rootCause}</div>
      </div>
      <div className="p-3">
        <div className="flex justify-between text-xs mb-2">
          <span className="text-gray-400">Action Items</span>
          <span>{progressPct}% complete</span>
        </div>
        {actionItems.map((a, i) => (
          <div key={i} className="flex items-center gap-2 text-xs py-0.5">
            <span>{a.done ? "✅" : "⬜"}</span>
            <span className={a.done ? "line-through text-gray-400" : ""}>{a.task}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
