"use client";

interface GalleryApp { name: string; icon: string; rating: number; }
interface GalleryCollection { id: string; title: string; description: string;
  icon: string; appCount: number; featured: boolean; apps: GalleryApp[]; }
interface AppGalleryGridProps { collections: GalleryCollection[];
  onSelect: (collectionId: string) => void; }

export function AppGalleryGrid({ collections, onSelect }: AppGalleryGridProps) {
  return (
    <div className="space-y-6">
      {collections.map(col => (
        <div key={col.id}>
          <button onClick={() => onSelect(col.id)}
            className="flex items-center gap-2 mb-2 hover:text-blue-600 transition">
            <span className="text-xl">{col.icon}</span>
            <h3 className="font-semibold">{col.title}</h3>
            <span className="text-xs text-gray-400">{col.appCount} apps</span>
            {col.featured && <span className="text-xs px-1.5 py-0.5 rounded bg-yellow-100 text-yellow-700">Featured</span>}
          </button>
          <p className="text-xs text-gray-400 mb-2">{col.description}</p>
          <div className="flex gap-2 overflow-x-auto">
            {col.apps.map(app => (
              <div key={app.name} className="shrink-0 w-24 rounded-lg border dark:border-gray-700 p-2 text-center">
                <span className="text-2xl">{app.icon}</span>
                <p className="text-xs font-medium mt-1 truncate">{app.name}</p>
                {app.rating > 0 && <p className="text-[10px] text-gray-400">⭐ {app.rating}</p>}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
