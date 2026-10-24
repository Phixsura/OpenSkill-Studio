"use client";

interface TzTime { timezone: string; offset: number; time: string; date: string; }
interface TimezoneClockStripProps { times: TzTime[]; }

const tzShort: Record<string, string> = {
  "UTC": "UTC", "US/Eastern": "EST", "US/Pacific": "PST",
  "Europe/London": "GMT", "Europe/Berlin": "CET", "Asia/Tokyo": "JST",
  "Asia/Shanghai": "CST", "Asia/Kolkata": "IST", "Australia/Sydney": "AEDT",
};

export function TimezoneClockStrip({ times }: TimezoneClockStripProps) {
  return (
    <div className="flex gap-3 overflow-x-auto pb-2">
      {times.map(t => (
        <div key={t.timezone} className="flex-shrink-0 rounded-lg border p-3 text-center dark:border-gray-700">
          <p className="text-2xl font-bold font-mono">{t.time}</p>
          <p className="text-xs font-medium">{tzShort[t.timezone] ?? t.timezone}</p>
          <p className="text-[10px] text-gray-400">UTC{t.offset >= 0 ? "+" : ""}{t.offset}</p>
        </div>
      ))}
    </div>
  );
}
