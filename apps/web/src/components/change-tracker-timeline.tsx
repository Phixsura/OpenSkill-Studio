"use client";

interface Change { id: number; entity: string; action: string; user: string; details: string; }
interface ChangeTrackerTimelineProps { changes: Change[]; total: number;
  byAction: Record<string, number>; }

const ACTION_ICONS: Record<string, string> = {
  deployed: "🚀", updated: "📝", created: "✨", deleted: "🗑️", scaled: "📈",
};

export function ChangeTrackerTimeline({ changes, total, byAction }: ChangeTrackerTimelineProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📋 Change Tracker</h3>
        <span className="text-xs text-gray-400">{total} changes</span>
      </div>
      <div className="divide-y dark:divide-gray-700 max-h-48 overflow-y-auto">
        {changes.map(c => (
          <div key={c.id} className="px-4 py-2">
            <div className="flex items-center gap-2 text-sm">
              <span>{ACTION_ICONS[c.action] ?? "⚙️"}</span>
              <span className="font-medium">{c.user}</span>
              <span className="text-gray-400">{c.action}</span>
              <span className="font-mono text-xs">{c.entity}</span>
            </div>
            {c.details && <div className="text-[10px] text-gray-400 ml-6">{c.details}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}
