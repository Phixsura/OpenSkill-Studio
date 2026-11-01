"use client";

interface MaintWindow { title: string; durationMin: number; affectedServices: string[];
  status: string; startDisplay: string; }
interface MaintWindowCalendarProps { windows: MaintWindow[]; inMaintenance: boolean;
  activeCount: number; upcoming: number; }

const STATUS_COLORS: Record<string, string> = {
  scheduled: "bg-blue-100 text-blue-700", active: "bg-yellow-100 text-yellow-700",
  completed: "bg-green-100 text-green-700", cancelled: "bg-gray-200 text-gray-500",
};

export function MaintWindowCalendar({ windows, inMaintenance, activeCount, upcoming }: MaintWindowCalendarProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔧 Maintenance Windows</h3>
        <div className="flex gap-2 text-xs">
          {inMaintenance && <span className="text-yellow-600 font-medium">⚠ Active Now</span>}
          <span className="text-gray-400">{upcoming} upcoming</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {windows.map((w, i) => (
          <div key={i} className="px-4 py-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium">{w.title}</span>
              <div className="flex gap-2">
                <span className="text-xs text-gray-400">{w.durationMin}min</span>
                <span className={`px-2 py-0.5 text-[10px] rounded-full ${STATUS_COLORS[w.status] ?? ""}`}>{w.status}</span>
              </div>
            </div>
            <div className="text-[10px] text-gray-400">{w.startDisplay} · {w.affectedServices.join(", ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
