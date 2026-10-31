"use client";

interface Counter { key: string; value: number; }
interface StatCounterDisplayProps { counters: Counter[]; total: number; }

export function StatCounterDisplay({ counters, total }: StatCounterDisplayProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">🔢 Counters</h3>
        <span className="text-xs text-gray-400">Total: {total.toLocaleString()}</span>
      </div>
      <div className="grid grid-cols-2 gap-2">
        {counters.map(c => (
          <div key={c.key} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
            <p className="text-xl font-bold">{c.value.toLocaleString()}</p>
            <p className="text-xs text-gray-400">{c.key.replace(/_/g, " ")}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
