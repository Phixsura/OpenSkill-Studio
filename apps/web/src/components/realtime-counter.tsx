"use client";

interface Counter { key: string; count: number; }
interface RealtimeCounterProps { counters: Counter[]; grandTotal: number; }

export function RealtimeCounterDisplay({ counters, grandTotal }: RealtimeCounterProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Realtime Counters</h3>
        <span className="text-lg font-bold">{grandTotal.toLocaleString()}</span>
      </div>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {counters.map(c => (
          <div key={c.key} className="rounded-lg border p-3 text-center dark:border-gray-700">
            <p className="text-2xl font-bold tabular-nums">{c.count.toLocaleString()}</p>
            <p className="mt-1 text-xs text-gray-400 font-mono">{c.key}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
