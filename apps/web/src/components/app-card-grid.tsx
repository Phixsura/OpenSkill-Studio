"use client";

interface AppCard { id: string; name: string; shortDescription: string; icon: string;
  stars: string; downloadsDisplay: string; category: string; verified: boolean; pricing: string; }
interface AppCardGridProps { cards: AppCard[]; onSelect: (id: string) => void; }

export function AppCardGrid({ cards, onSelect }: AppCardGridProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {cards.map(c => (
        <button key={c.id} onClick={() => onSelect(c.id)}
          className="rounded-xl border p-4 text-left hover:shadow-md transition dark:border-gray-700">
          <div className="flex items-start gap-3">
            <span className="text-3xl">{c.icon}</span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1">
                <h4 className="text-sm font-bold truncate">{c.name}</h4>
                {c.verified && <span className="text-blue-500 text-xs">✓</span>}
              </div>
              <p className="text-xs text-gray-500 line-clamp-2 mt-0.5">{c.shortDescription}</p>
              <div className="mt-2 flex items-center justify-between">
                <span className="text-xs text-yellow-500">{c.stars}</span>
                <span className="text-xs text-gray-400">{c.downloadsDisplay}</span>
                <span className="text-xs font-medium text-blue-600">{c.pricing}</span>
              </div>
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}
