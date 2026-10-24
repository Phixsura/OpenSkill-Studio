"use client";

interface Release { version: string; targetDate: string; featureCount: number;
  owner: string; status: string; }
interface ReleaseCalendarProps { releases: Release[]; planned: number;
  inProgress: number; released: number; totalFeatures: number; }

const STATUS_COLORS: Record<string, string> = {
  planned: "bg-gray-100 text-gray-700", in_progress: "bg-blue-100 text-blue-700",
  released: "bg-green-100 text-green-700",
};

export function ReleaseCalendar({ releases, planned, inProgress, released, totalFeatures }: ReleaseCalendarProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📅 Release Calendar</h3>
        <div className="flex gap-2 text-xs">
          <span className="text-green-600">{released} released</span>
          <span className="text-blue-600">{inProgress} in progress</span>
          <span className="text-gray-400">{planned} planned</span>
        </div>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {releases.map(r => (
          <div key={r.version} className="flex items-center justify-between px-4 py-2.5">
            <div>
              <span className="text-sm font-bold">v{r.version}</span>
              <span className="text-xs text-gray-400 ml-2">{r.targetDate} · {r.featureCount} features</span>
            </div>
            <span className={`px-2 py-0.5 text-[10px] rounded-full ${STATUS_COLORS[r.status] ?? ""}`}>
              {r.status.replaceAll("_", " ")}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
