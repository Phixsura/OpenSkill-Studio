"use client";

interface StatCard { id: string; label: string; value: number; icon: string;
  format?: string; change: number; }
interface DeveloperStatsGridProps { cards: StatCard[]; }

export function DeveloperStatsGrid({ cards }: DeveloperStatsGridProps) {
  const fmt = (val: number, format?: string) =>
    format === "currency" ? `$${val.toLocaleString()}` : val.toLocaleString();

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      {cards.map(c => (
        <div key={c.id} className="rounded-lg border p-3 text-center dark:border-gray-700">
          <span className="text-2xl">{c.icon}</span>
          <p className="mt-1 text-xl font-bold">{fmt(c.value, c.format)}</p>
          <p className="text-xs text-gray-400">{c.label}</p>
          {c.change !== 0 && (
            <p className={`text-xs ${c.change > 0 ? "text-green-500" : "text-red-500"}`}>
              {c.change > 0 ? "↑" : "↓"} {Math.abs(c.change).toLocaleString()}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
