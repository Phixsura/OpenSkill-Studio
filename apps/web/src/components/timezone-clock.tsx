"use client";

interface TzTime { fromTz: string; toTz: string; toHour: number; display: string; dayChange: string; }
interface TimezoneClockProps { fromTz: string; fromHour: number; teamTimes: TzTime[]; }

export function TimezoneClock({ fromTz, fromHour, teamTimes }: TimezoneClockProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-1">🌍 Team Times</h3>
      <p className="text-xs text-gray-400 mb-3">{fromHour}:00 {fromTz}</p>
      <div className="grid grid-cols-3 gap-3">
        {teamTimes.map(t => (
          <div key={t.toTz} className="text-center rounded-lg bg-gray-50 dark:bg-gray-800 p-3">
            <p className="text-2xl font-bold font-mono">{String(t.toHour).padStart(2, "0")}:00</p>
            <p className="text-xs text-gray-400">{t.toTz}</p>
            {t.dayChange !== "same_day" && (
              <p className="text-[10px] text-yellow-500">{t.dayChange === "next_day" ? "+1 day" : "-1 day"}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
