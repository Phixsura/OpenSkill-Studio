"use client";

interface ApiPulseWidgetProps { healthy: number; total: number; avgLatencyMs: number;
  totalRps: number; errorCount: number; pulse: string; }

const PULSE_STYLES: Record<string, { color: string; icon: string }> = {
  strong: { color: "text-green-600", icon: "💚" },
  weak: { color: "text-yellow-600", icon: "💛" },
  critical: { color: "text-red-600", icon: "❤️" },
};

export function ApiPulseWidget({ healthy, total, avgLatencyMs, totalRps, errorCount, pulse }: ApiPulseWidgetProps) {
  const s = PULSE_STYLES[pulse] ?? PULSE_STYLES.strong;
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">{s.icon} API Pulse</h3>
        <span className={`text-xs font-medium ${s.color}`}>{pulse} · {healthy}/{total}</span>
      </div>
      <div className="grid grid-cols-3 gap-px bg-gray-200 dark:bg-gray-700">
        {[{ l: "Latency", v: `${avgLatencyMs}ms` }, { l: "RPS", v: totalRps.toLocaleString() },
          { l: "Errors", v: errorCount }].map(m => (
          <div key={m.l} className="bg-white dark:bg-gray-900 p-3 text-center">
            <div className="text-sm font-bold">{m.v}</div>
            <div className="text-[9px] text-gray-400">{m.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
