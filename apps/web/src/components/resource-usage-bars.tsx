"use client";

interface ResourceUsageBarsProps { cpuPct: number; memoryMb: number; memoryLimitMb: number; networkKb: number; networkLimitKb: number; }

export function ResourceUsageBars({ cpuPct, memoryMb, memoryLimitMb, networkKb, networkLimitKb }: ResourceUsageBarsProps) {
  const memPct = Math.min(100, (memoryMb / memoryLimitMb) * 100);
  const netPct = Math.min(100, (networkKb / networkLimitKb) * 100);
  const barColor = (pct: number) => pct > 90 ? "bg-red-500" : pct > 70 ? "bg-yellow-500" : "bg-green-500";

  const bars = [
    { label: "CPU", pct: cpuPct, detail: `${cpuPct}%` },
    { label: "Memory", pct: memPct, detail: `${memoryMb}MB / ${memoryLimitMb}MB` },
    { label: "Network", pct: netPct, detail: `${networkKb}KB / ${networkLimitKb}KB` },
  ];

  return (
    <div className="space-y-3 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">Resource Usage</h3>
      {bars.map(b => (
        <div key={b.label}>
          <div className="flex justify-between text-xs">
            <span>{b.label}</span><span className="text-gray-400">{b.detail}</span>
          </div>
          <div className="mt-1 h-2 rounded-full bg-gray-200 dark:bg-gray-700">
            <div className={`h-full rounded-full ${barColor(b.pct)}`} style={{ width: `${b.pct}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}
