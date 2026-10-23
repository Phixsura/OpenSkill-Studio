"use client";

interface TimelineEvent { type: string; message?: string; }
interface IncidentTimelineCardProps { title: string; severity: string;
  status: string; events: TimelineEvent[]; durationMin: number; }

const SEV_COLORS: Record<string, string> = {
  critical: "bg-red-500", major: "bg-orange-500", minor: "bg-yellow-500", info: "bg-blue-500",
};
const EVT_ICONS: Record<string, string> = {
  triggered: "🔴", acknowledged: "👁️", investigating: "🔍", resolved: "✅", update: "📝",
};

export function IncidentTimelineCard({ title, severity, status, events, durationMin }: IncidentTimelineCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-sm">{title}</h3>
          <div className="flex gap-2">
            <span className={`px-2 py-0.5 text-[10px] text-white rounded-full ${SEV_COLORS[severity] ?? "bg-gray-500"}`}>{severity}</span>
            <span className="text-xs text-gray-400">{status}</span>
          </div>
        </div>
        <div className="text-xs text-gray-400 mt-1">{durationMin} min · {events.length} events</div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {events.map((e, i) => (
          <div key={i} className="flex items-center gap-2 px-4 py-2 text-xs">
            <span>{EVT_ICONS[e.type] ?? "⚪"}</span>
            <span className="capitalize font-medium">{e.type}</span>
            {e.message && <span className="text-gray-400 truncate">{e.message}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
