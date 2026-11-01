"use client";

interface RecommendedApp { id: string; name: string; icon: string; category: string;
  rating: number; reason: string; }
interface DiscoveryCarouselProps { recommendations: RecommendedApp[]; basedOn: string[];
  onSelect: (id: string) => void; }

export function DiscoveryCarousel({ recommendations, basedOn, onSelect }: DiscoveryCarouselProps) {
  if (recommendations.length === 0) return null;
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">💡 Recommended for You</h2>
        <span className="text-xs text-gray-400">Based on: {basedOn.join(", ")}</span>
      </div>
      <div className="flex gap-3 overflow-x-auto pb-2">
        {recommendations.map(a => (
          <button key={a.id} onClick={() => onSelect(a.id)}
            className="flex shrink-0 flex-col items-center gap-2 rounded-xl border p-4 w-32 hover:shadow dark:border-gray-700">
            <span className="text-3xl">{a.icon}</span>
            <p className="text-xs font-medium text-center truncate w-full">{a.name}</p>
            <span className="text-xs text-yellow-500">⭐ {a.rating}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
