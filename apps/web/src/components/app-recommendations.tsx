"use client";

interface RecommendedApp { id: string; name: string; icon?: string; rating: number;
  reason?: string; recommendationScore?: number; }
interface AppRecommendationsProps { title: string; apps: RecommendedApp[];
  onSelect: (id: string) => void; }

export function AppRecommendations({ title, apps, onSelect }: AppRecommendationsProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-5">
      <h3 className="font-semibold mb-3">{title}</h3>
      <div className="grid grid-cols-3 gap-3">
        {apps.map(a => (
          <button key={a.id} onClick={() => onSelect(a.id)}
            className="rounded-lg border dark:border-gray-700 p-3 text-center hover:shadow-lg transition">
            <span className="text-2xl">{a.icon || "📱"}</span>
            <p className="text-sm font-medium mt-1 truncate">{a.name}</p>
            <p className="text-xs text-yellow-500">⭐ {a.rating}</p>
            {a.reason && <p className="text-xs text-gray-400 mt-0.5 truncate">{a.reason}</p>}
          </button>
        ))}
      </div>
    </div>
  );
}
