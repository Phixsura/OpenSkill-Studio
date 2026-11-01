"use client";

interface ResponseTimeGraphProps { avg: number; p50: number; p95: number;
  p99: number; slaPct: number; slaMet: boolean; status: string; slams: number; }

export function ResponseTimeGraph({ avg, p50, p95, p99, slaPct, slaMet, status, slams }: ResponseTimeGraphProps) {
  const bars = [
    { label: "Avg", value: avg }, { label: "P50", value: p50 },
    { label: "P95", value: p95 }, { label: "P99", value: p99 },
  ];
  const maxVal = Math.max(...bars.map(b => b.value), 1);
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">⏱️ Response Time</h3>
        <div className="flex items-center gap-2">
          <span className={`text-xs px-2 py-0.5 rounded-full ${
            status === "fast" ? "bg-green-100 text-green-700" :
            status === "ok" ? "bg-yellow-100 text-yellow-700" : "bg-red-100 text-red-700"
          }`}>{status}</span>
          <span className={`text-xs ${slaMet ? "text-green-600" : "text-red-500"}`}>
            SLA: {slaPct}%
          </span>
        </div>
      </div>
      <div className="flex items-end gap-4 h-20 mb-2">
        {bars.map(b => (
          <div key={b.label} className="flex-1 flex flex-col items-center">
            <div className={`w-full rounded-t ${b.value > slams ? "bg-red-400" : "bg-blue-500"}`}
                 style={{ height: `${(b.value / maxVal) * 100}%` }} />
            <span className="text-[10px] text-gray-400 mt-1">{b.label}</span>
            <span className="text-xs font-mono">{b.value}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
}
