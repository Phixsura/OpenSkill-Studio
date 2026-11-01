"use client";

interface OncallInfo { oncall: string; rotation: string; daysRemaining: number; nextOncall: string; }
interface OncallScheduleProps { oncalls: OncallInfo[]; }

export function OncallSchedule({ oncalls }: OncallScheduleProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📟 On-Call Schedule</h3>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {oncalls.map(o => (
          <div key={o.rotation} className="flex items-center justify-between px-4 py-3">
            <div>
              <div className="text-sm font-medium">{o.rotation}</div>
              <div className="text-[10px] text-gray-400">{o.daysRemaining}d remaining · next: {o.nextOncall}</div>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-sm font-medium">{o.oncall}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
