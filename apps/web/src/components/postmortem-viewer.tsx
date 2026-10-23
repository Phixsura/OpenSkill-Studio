"use client";

interface TimelineEntry { time: string; action: string; by: string; }
interface ActionItem { task: string; owner: string; priority: string; due: string; }
interface PostmortemViewerProps { title: string; severity: string; mttrDisplay: string;
  impact: string; rootCause: string; timeline: TimelineEntry[];
  actionItems: ActionItem[]; authors: string[]; }

const SEV: Record<string, string> = { sev1: "bg-red-100 text-red-700", sev2: "bg-orange-100 text-orange-700", sev3: "bg-yellow-100 text-yellow-700" };
const PRI: Record<string, string> = { high: "text-red-600", medium: "text-yellow-600", low: "text-gray-400" };

export function PostmortemViewer({ title, severity, mttrDisplay, impact, rootCause, timeline, actionItems, authors }: PostmortemViewerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden max-w-2xl">
      <div className="p-5 border-b dark:border-gray-700">
        <div className="flex items-center justify-between mb-1">
          <h2 className="text-lg font-bold">{title}</h2>
          <span className={`text-xs px-2 py-0.5 rounded-full ${SEV[severity] || ""}`}>{severity}</span>
        </div>
        <div className="flex gap-3 text-xs text-gray-400">
          <span>MTTR: {mttrDisplay}</span>
          <span>By: {authors.join(", ")}</span>
        </div>
      </div>
      <div className="p-5 space-y-4">
        <div><h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Impact</h4><p className="text-sm">{impact}</p></div>
        <div><h4 className="text-xs font-semibold text-gray-400 uppercase mb-1">Root Cause</h4><p className="text-sm">{rootCause}</p></div>
        <div>
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Timeline</h4>
          <div className="border-l-2 border-gray-200 dark:border-gray-700 space-y-2 pl-4">
            {timeline.map((t, i) => (
              <div key={i} className="text-sm">
                <span className="font-mono text-xs text-gray-400 mr-2">{t.time}</span>
                <span>{t.action}</span>
                <span className="text-xs text-gray-400 ml-1">— {t.by}</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Action Items ({actionItems.length})</h4>
          {actionItems.map((a, i) => (
            <div key={i} className="flex justify-between text-sm py-1">
              <span className={PRI[a.priority] || ""}>{a.task}</span>
              <span className="text-xs text-gray-400">{a.owner} {a.due && `· ${a.due}`}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
