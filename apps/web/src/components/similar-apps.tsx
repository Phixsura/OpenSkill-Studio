"use client";

interface SimilarApp { id: string; name: string; icon: string; category: string; rating: number; }
interface SimilarAppsProps { apps: SimilarApp[]; onSelect: (id: string) => void; }

export function SimilarApps({ apps, onSelect }: SimilarAppsProps) {
  if (apps.length === 0) return null;
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">Similar Apps</h3>
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {apps.map(a => (
          <button key={a.id} onClick={() => onSelect(a.id)}
            className="flex items-center gap-3 rounded-lg border p-3 text-left hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800">
            <span className="text-2xl">{a.icon}</span>
            <div>
              <p className="text-sm font-medium">{a.name}</p>
              <div className="flex gap-2 text-xs text-gray-400">
                <span>⭐ {a.rating}</span>
                <span className="capitalize">{a.category}</span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
