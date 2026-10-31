"use client";

interface SecretSchedule { secret_id: string; name: string; age_days: number; max_age_days: number;
  needs_rotation: boolean; days_until_rotation: number; urgency: string; }
interface SecretRotationScheduleProps { schedule: SecretSchedule[]; overdueCount: number; onRotate: (id: string) => void; }

const urgencyStyle: Record<string, string> = {
  critical: "bg-red-100 text-red-700 dark:bg-red-900/30", soon: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30",
  ok: "bg-green-100 text-green-700 dark:bg-green-900/30",
};

export function SecretRotationSchedule({ schedule, overdueCount, onRotate }: SecretRotationScheduleProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Secret Rotation</h2>
        {overdueCount > 0 && (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30">
            {overdueCount} overdue
          </span>
        )}
      </div>
      <div className="space-y-2">
        {schedule.map(s => (
          <div key={s.secret_id} className="flex items-center justify-between rounded-lg border p-3 dark:border-gray-700">
            <div>
              <p className="font-medium">{s.name}</p>
              <p className="text-xs text-gray-400">Age: {s.age_days}d / {s.max_age_days}d max</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`rounded-full px-2 py-0.5 text-xs ${urgencyStyle[s.urgency] ?? ""}`}>{s.urgency}</span>
              {s.needs_rotation && (
                <button onClick={() => onRotate(s.secret_id)} className="rounded bg-red-600 px-2 py-1 text-xs text-white">Rotate Now</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
