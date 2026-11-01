"use client";

interface DedupStatusCardProps { totalTracked: number; activeWindow: number;
  duplicatesBlocked: number; windowSec: number; }

export function DedupStatusCard({ totalTracked, activeWindow, duplicatesBlocked, windowSec }: DedupStatusCardProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Request Deduplication</h3>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Tracked", v: totalTracked }, { l: "Active", v: activeWindow },
          { l: "Blocked", v: duplicatesBlocked }, { l: "Window", v: `${windowSec}s` }].map(s => (
          <div key={s.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-lg font-bold">{s.v}</div>
            <div className="text-[10px] text-gray-400">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
