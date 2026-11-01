"use client";

interface RecExt { extensionId: string; name: string; category: string; installs: number; rating: number; }

export function RecommendationCarousel({ recommendations, title, onSelect }: {
  recommendations: RecExt[]; title: string; onSelect?: (id: string) => void;
}) {
  if (!recommendations.length) return null;
  return (
    <div className="space-y-2">
      <h3 className="font-bold text-sm">{title}</h3>
      <div className="flex gap-2 overflow-x-auto pb-2">
        {recommendations.map(r => (
          <button key={r.extensionId} onClick={() => onSelect?.(r.extensionId)}
            className="shrink-0 w-40 border dark:border-gray-700 rounded-xl p-3 text-left hover:border-blue-400">
            <span className="font-medium text-sm block truncate">{r.name}</span>
            <span className="text-xs text-gray-500 block">{r.category}</span>
            <div className="flex justify-between mt-1 text-xs">
              <span className="text-yellow-500">{"★".repeat(Math.round(r.rating))}</span>
              <span className="text-gray-400">{r.installs}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
