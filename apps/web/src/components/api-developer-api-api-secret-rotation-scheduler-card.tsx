"use client";

interface ScheduleInfo { secret_id: string; secret_type: string; days_until_rotation: number; rotation_count: number; overdue: boolean; }
interface Props { schedules: ScheduleInfo[]; overdueCount: number; appName: string; }

const typeIcon: Record<string, string> = { api_key: "🔑", webhook_secret: "🔐", jwt_signing_key: "📜" };

export default function APIDeveloperAPIApiSecretRotationSchedulerCard({ schedules, overdueCount, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔄 Secret Rotation</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {overdueCount > 0 && <span className="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-bold text-red-700">{overdueCount} overdue</span>}
      </div>
      {schedules.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No rotation schedules</p>
      ) : (
        <div className="space-y-1.5">
          {schedules.map((s) => (
            <div key={s.secret_id} className="flex items-center justify-between text-[11px]">
              <div className="flex items-center gap-1.5">
                <span>{typeIcon[s.secret_type] ?? "•"}</span>
                <span className="text-gray-700 dark:text-gray-300">{s.secret_id}</span>
              </div>
              <span className={s.overdue ? "text-red-500 font-bold" : "text-gray-400"}>{s.overdue ? "OVERDUE" : `${s.days_until_rotation}d`} · {s.rotation_count}×</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
