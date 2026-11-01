"use client";

interface ErrRecoveryPanelProps { totalEvents: number; autoRecovered: number;
  autoPct: number; byStrategy: Record<string, number>; }

const STRAT_ICONS: Record<string, string> = {
  retry: "🔄", fallback: "🔀", circuit_break: "⚡", alert: "🚨", rollback: "⏪",
};

export function ErrRecoveryPanel({ totalEvents, autoRecovered, autoPct, byStrategy }: ErrRecoveryPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔧 Error Recovery</h3>
        <span className="text-xs text-gray-400">{totalEvents} events · {autoPct}% auto-recovered</span>
      </div>
      <div className="grid grid-cols-2 gap-px bg-gray-200 dark:bg-gray-700 border-b dark:border-gray-700">
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold text-green-600">{autoRecovered}</div>
          <div className="text-[10px] text-gray-400">Auto Recovered</div>
        </div>
        <div className="bg-white dark:bg-gray-900 p-3 text-center">
          <div className="text-lg font-bold">{totalEvents - autoRecovered}</div>
          <div className="text-[10px] text-gray-400">Manual</div>
        </div>
      </div>
      <div className="p-3">
        {Object.entries(byStrategy).map(([s, c]) => (
          <div key={s} className="flex justify-between text-xs py-0.5">
            <span>{STRAT_ICONS[s] ?? "⚙️"} {s.replaceAll("_", " ")}</span>
            <span className="text-gray-400">{c}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
