"use client";

interface Signal { value: number; unit: string; ok: boolean; }
interface GoldenSignalsProps { latency: Signal; traffic: Signal;
  errors: Signal; saturation: Signal; status: string; score: number; }

const SIGNAL_ICONS: Record<string, string> = {
  latency: "⏱️", traffic: "📊", errors: "🐛", saturation: "📈",
};

export function GoldenSignals({ latency, traffic, errors, saturation, status, score }: GoldenSignalsProps) {
  const signals = { latency, traffic, errors, saturation };
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🌟 Golden Signals</h3>
        <span className={`text-xs font-medium ${status === "healthy" ? "text-green-600" : status === "degraded" ? "text-yellow-600" : "text-red-600"}`}>
          {score}/4 · {status}
        </span>
      </div>
      <div className="grid grid-cols-4 gap-px bg-gray-200 dark:bg-gray-700">
        {Object.entries(signals).map(([name, sig]) => (
          <div key={name} className={`bg-white dark:bg-gray-900 p-3 text-center ${!sig.ok ? "bg-red-50 dark:bg-red-900/10" : ""}`}>
            <div className="text-lg">{SIGNAL_ICONS[name]}</div>
            <div className="text-sm font-bold">{sig.value}{sig.unit}</div>
            <div className="text-[9px] text-gray-400 capitalize">{name}</div>
            <div className="text-[10px]">{sig.ok ? "✅" : "⚠️"}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
