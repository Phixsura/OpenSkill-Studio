"use client";

interface StatCounter { key: string; value: number; label: string; icon: string; format: string; }
interface StatCounterRowProps { counters: StatCounter[]; }

function fmt(val: number, format: string): string {
  switch (format) {
    case "compact":
      return val >= 1e6 ? `${(val / 1e6).toFixed(1)}M` : val >= 1e3 ? `${(val / 1e3).toFixed(1)}K` : String(val);
    case "currency": return `$${val.toLocaleString()}`;
    case "percentage": return `${val}%`;
    case "decimal": return val.toFixed(1);
    default: return val.toLocaleString();
  }
}

export function StatCounterRow({ counters }: StatCounterRowProps) {
  return (
    <div className="grid gap-3" style={{ gridTemplateColumns: `repeat(${Math.min(counters.length, 6)}, 1fr)` }}>
      {counters.map(c => (
        <div key={c.key} className="rounded-lg border p-4 text-center dark:border-gray-700">
          <span className="text-2xl">{c.icon}</span>
          <p className="mt-2 text-2xl font-black">{fmt(c.value, c.format)}</p>
          <p className="text-xs text-gray-400">{c.label}</p>
        </div>
      ))}
    </div>
  );
}
