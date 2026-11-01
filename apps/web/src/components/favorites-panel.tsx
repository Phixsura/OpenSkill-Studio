"use client";

interface FavoriteExt { extensionId: string; name: string; icon: string; pinned: boolean; accessCount: number; }

export function FavoritesPanel({ favorites, onRemove, onTogglePin }: {
  favorites: FavoriteExt[];
  onRemove?: (id: string) => void;
  onTogglePin?: (id: string) => void;
}) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-bold">⭐ Favorites</h2>
      <div className="space-y-1">
        {favorites.map((f) => (
          <div key={f.extensionId} className="rounded-lg border dark:border-gray-700 p-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button onClick={() => onTogglePin?.(f.extensionId)}
                className={`text-sm ${f.pinned ? "text-yellow-500" : "text-gray-300"}`}>
                {f.pinned ? "📌" : "○"}
              </button>
              <span className="text-lg">{f.icon}</span>
              <span className="font-semibold text-sm">{f.name}</span>
              {f.accessCount > 0 && <span className="text-xs text-gray-400">×{f.accessCount}</span>}
            </div>
            <button onClick={() => onRemove?.(f.extensionId)} className="text-xs text-red-500">✕</button>
          </div>
        ))}
        {favorites.length === 0 && <p className="text-sm text-gray-500">No favorites yet</p>}
      </div>
    </div>
  );
}
