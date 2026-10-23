"use client";

interface Recommendation { id: string; name: string; category?: string; rating?: number; reason: string; }
interface RecommendationCarouselProps { recommendations: Recommendation[]; onInstall: (id: string) => void; }

const reasonLabels: Record<string, string> = {
  category_match: "Similar to your apps", popular: "Popular", trending: "Trending",
};

export function RecommendationCarousel({ recommendations, onInstall }: RecommendationCarouselProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Recommended for You</h2>
      <div className="flex gap-3 overflow-x-auto pb-2">
        {recommendations.map(r => (
          <div key={r.id} className="w-48 flex-shrink-0 rounded-lg border p-3 dark:border-gray-700">
            <p className="font-medium">{r.name}</p>
            {r.category && <p className="text-xs text-gray-400">{r.category}</p>}
            {r.rating && <p className="text-xs text-yellow-500">{"★".repeat(Math.round(r.rating))}</p>}
            <p className="mt-1 text-xs text-blue-500">{reasonLabels[r.reason] ?? r.reason}</p>
            <button onClick={() => onInstall(r.id)}
              className="mt-2 w-full rounded bg-blue-600 py-1 text-xs text-white">Install</button>
          </div>
        ))}
      </div>
    </div>
  );
}
