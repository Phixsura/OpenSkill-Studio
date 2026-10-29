"use client";

interface ScheduleInfo { schedule_id: string; version: string; title: string; publish_date: string; status: string; }
interface Props { schedules: ScheduleInfo[]; appName: string; }

const sStyle: Record<string, string> = {
  scheduled: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  published: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
  cancelled: "bg-gray-100 text-gray-500 dark:bg-gray-800",
};

export default function APIChangelogScheduleCard({ schedules, appName }: Props) {
  const upcoming = schedules.filter((s) => s.status === "scheduled").length;
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📅 Changelog Schedule</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{upcoming} upcoming</span>
      </div>
      {schedules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No scheduled releases</p>
      ) : (
        <div className="space-y-1.5">
          {schedules.map((s) => (
            <div key={s.schedule_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${sStyle[s.status] ?? ""}`}>{s.status}</span>
                <span className="text-gray-700 dark:text-gray-300">{s.title}</span>
              </div>
              <span className="text-gray-400">{s.publish_date}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
