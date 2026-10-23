"use client";

interface KpiCard { key: string; label: string; icon: string; display: string;
  deltaDisplay: string | null; trend: string | null; positive: boolean | null; }
interface KpiCardsRowProps { cards: KpiCard[]; }

export function KpiCardsRow({ cards }: KpiCardsRowProps) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map(c => (
        <div key={c.key} className="rounded-xl border p-4 dark:border-gray-700">
          <div className="flex items-center justify-between mb-1">
            <span className="text-lg">{c.icon}</span>
            {c.deltaDisplay && (
              <span className={`text-xs font-medium ${c.positive ? "text-green-600" : c.positive === false ? "text-red-600" : "text-gray-400"}`}>
                {c.trend === "up" ? "↑" : c.trend === "down" ? "↓" : "→"} {c.deltaDisplay}
              </span>
            )}
          </div>
          <p className="text-xl font-bold">{c.display}</p>
          <p className="text-xs text-gray-400">{c.label}</p>
        </div>
      ))}
    </div>
  );
}
