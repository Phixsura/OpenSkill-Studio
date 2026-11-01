"use client";
interface Signal { label: string; value: string; ok: boolean; }
interface GoldenSignalsPanelProps { status: string; signals: Signal[]; }
export function GoldenSignalsPanel({ status, signals }: GoldenSignalsPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className={`p-3 text-white text-center text-sm font-bold ${status === "healthy" ? "bg-green-500" : "bg-yellow-500"}`}>
        Golden Signals: {status.toUpperCase()}
      </div>
      <div className="grid grid-cols-4 gap-2 p-4 text-center text-xs">
        {signals.map(s => (
          <div key={s.label}>
            <div className="text-gray-400 mb-0.5">{s.label}</div>
            <div className={`font-bold text-lg ${s.ok ? "text-green-600" : "text-red-500"}`}>{s.value}</div>
            <div className="text-[10px]">{s.ok ? "✅" : "❌"}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
