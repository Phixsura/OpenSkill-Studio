"use client";

interface RtMetricStreamProps { stream: string; latest: number; avg: number;
  min: number; max: number; count: number; }

export function RtMetricStream({ stream, latest, avg, min, max, count }: RtMetricStreamProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📡 {stream}</h3>
        <span className="text-xs text-gray-400">{count} points</span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Latest", v: latest }, { l: "Avg", v: avg },
          { l: "Min", v: min }, { l: "Max", v: max }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold font-mono">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
